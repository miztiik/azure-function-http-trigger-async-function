import json
import logging
import datetime
import os
import random
import uuid

import asyncio

import azure.functions as func
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore


GREEN_COLOR = "\033[32m"
RED_COLOR = "\033[31m"
RESET_COLOR = "\033[0m"


# Example usage with logging
logging.info(f'{GREEN_COLOR}This is green text{RESET_COLOR}')

class GlobalArgs:
    OWNER = "Mystique"
    VERSION = "2023-05-23"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    EVNT_WEIGHTS = {"success": 80, "fail": 20}
    TRIGGER_RANDOM_FAILURES = os.getenv("TRIGGER_RANDOM_FAILURES", True)
    WAIT_SECS_BETWEEN_MSGS = int(os.getenv("WAIT_SECS_BETWEEN_MSGS", 2))
    TOT_MSGS_TO_PRODUCE = int(os.getenv("TOT_MSGS_TO_PRODUCE", 10))

    SA_NAME = os.getenv("SA_NAME", "warehouse7rfk2o005")
    BLOB_SVC_ACCOUNT_URL = os.getenv("BLOB_SVC_ACCOUNT_URL","https://warehousefa3mwu001.blob.core.windows.net")
    BLOB_NAME = os.getenv("BLOB_NAME", "store-events-blob-001")
    BLOB_PREFIX = "sales_events"

    COSMOS_DB_URL = os.getenv("COSMOS_DB_URL", "https://warehouse-cosmos-db-005.documents.azure.com:443/")
    COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "warehouse-cosmos-db-005")
    COSMOS_DB_CONTAINER_NAME = os.getenv("COSMOS_DB_CONTAINER_NAME", "warehouse-cosmos-db-container-005")
    
    SVC_BUS_FQDN = os.getenv("SVC_BUS_FQDN", "warehouse-q-svc-bus-ns-002.servicebus.windows.net")
    SVC_BUS_Q_NAME = os.getenv("SVC_BUS_Q_NAME","warehouse-q-svc-bus-q-002")

    MSG_COUNT = 0
    MAX_MESSAGES_TO_PROCESS = 15
    EVENT_HUB_FQDN = os.getenv("EVENT_HUB_FQDN", "warehouse-event-hub-ns-partition-processor-001.servicebus.windows.net")
    EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME","store-events-stream-001")
    EVENT_HUB_SALE_EVENTS_CONSUMER_GROUP_NAME = os.getenv("EVENT_HUB_SALE_EVENTS_CONSUMER_GROUP_NAME","sale-events-consumers-001")

def _rand_coin_flip():
    r = False
    if os.getenv("TRIGGER_RANDOM_FAILURES", True):
        if random.randint(1, 100) > 90:
            r = True
    return r

def _gen_uuid():
    return str(uuid.uuid4())

def write_to_blob(container_prefix: str, data: dict, blob_svc_client):
    try:
        blob_name = f"{GlobalArgs.BLOB_PREFIX}/event_type={container_prefix}/dt={datetime.datetime.now().strftime('%Y_%m_%d')}/{datetime.datetime.now().strftime('%s%f')}.json"
        if container_prefix is None:
            blob_name = f"{GlobalArgs.BLOB_PREFIX}/dt={datetime.datetime.now().strftime('%Y_%m_%d')}/{datetime.datetime.now().strftime('%s%f')}.json"
        resp = blob_svc_client.get_blob_client(container=f"{GlobalArgs.BLOB_NAME}", blob=blob_name).upload_blob(json.dumps(data).encode("UTF-8"))
        logging.info(f"Blob {GREEN_COLOR}{blob_name}{RESET_COLOR} uploaded successfully")
        logging.debug(f"{resp}")
    except Exception as e:
        logging.exception(f"ERROR:{str(e)}")

def write_to_cosmosdb(data: dict, db_container):
    try:
        data["id"] = data.pop("request_id", None)
        resp = db_container.create_item(body=data)
        # db_container.create_item(body={'id': str(random.randrange(100000000)), 'ts': str(datetime.datetime.now())})
        logging.info(f"Document with id {GREEN_COLOR}{data['id']}{RESET_COLOR} written to CosmosDB successfully")
    except Exception as e:
        logging.exception(f"ERROR:{str(e)}")

msg_count = 0
async def on_event(partition_context, event):
    global msg_count, client
    msg_count += 1
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print("Received event: {}".format(event.body_as_str()))
    print("Properties: {}".format(event.properties))
    print("System properties: {}".format(event.system_properties))
    print(f"Message Count: {msg_count} of {GlobalArgs.MAX_MESSAGES_TO_PROCESS}")
    if msg_count >= GlobalArgs.MAX_MESSAGES_TO_PROCESS:
        await partition_context.update_checkpoint(event)
        print("Updated checkpoint at {}".format(event.offset))
        print("Exiting receive handler...")
        await client.close()

async def receive(client):
    await client.receive(
        on_event=on_event,
        starting_position="-1",
        partition_id="1"
    )

async def receive_events():
    global client
    azure_log_level = logging.getLogger("azure").setLevel(logging.ERROR)
    credential = DefaultAzureCredential(logging_enable=True, logging=azure_log_level)
    checkpoint_store = BlobCheckpointStore(
        blob_account_url=GlobalArgs.BLOB_SVC_ACCOUNT_URL,
        container_name=GlobalArgs.BLOB_NAME,
        credential=credential,
    )
    client = EventHubConsumerClient(
        fully_qualified_namespace=GlobalArgs.EVENT_HUB_FQDN,
        eventhub_name=GlobalArgs.EVENT_HUB_NAME,
        consumer_group=GlobalArgs.EVENT_HUB_SALE_EVENTS_CONSUMER_GROUP_NAME,
        checkpoint_store=checkpoint_store,
        credential=credential,
    )
    async with client:
        await receive(client)
    

async def main():
# def main(req: func.HttpRequest) -> func.HttpResponse:
    _a_resp = {"status": False,
               "miztiik_event_processed": False}
    
    recv_cnt={}
    req_body={}

    try:
        # try:
        #     recv_cnt = req.params.get("count")
        #     if recv_cnt:
        #         recv_cnt = int(recv_cnt)
        #     logging.info(f"got from params: {recv_cnt}")
        # except ValueError:
        #     pass
        # if not recv_cnt:
        #     try:
        #         req_body = req.get_json()
        #     except ValueError:
        #         _a_resp["msg"] = "count not found in body"
        #         logging.info("count not found in body")
        #         pass
        #     else:
        #         recv_cnt = int(req_body.get("count"))

        # logging.info(f"Received Event: {recv_cnt}")

        # if recv_cnt:
        #     GlobalArgs.MAX_MESSAGES_TO_PROCESS = recv_cnt
    
        resp =  await receive_events()

        azure_log_level = logging.getLogger("azure").setLevel(logging.ERROR)
        default_credential = DefaultAzureCredential(logging_enable=False,logging=azure_log_level)

        blob_svc_client = BlobServiceClient(GlobalArgs.BLOB_SVC_ACCOUNT_URL, credential=default_credential, logging=azure_log_level)
        
        cosmos_client = CosmosClient(url=GlobalArgs.COSMOS_DB_URL, credential=default_credential)
        db_client = cosmos_client.get_database_client(GlobalArgs.COSMOS_DB_NAME)
        db_container = db_client.get_container_client(GlobalArgs.COSMOS_DB_CONTAINER_NAME)

        # write to blob
        # _evnt_type=event.metadata["Properties"].get("event_type")
        # write_to_blob(container_prefix=_evnt_type, data=recv_body, blob_svc_client=blob_svc_client)

        # # write to cosmosdb
        # write_to_cosmosdb(recv_body, db_container)

        print("all done")

        _a_resp["status"] = True
        _a_resp["miztiik_event_processed"] = True
        _a_resp["last_processed_on"] = datetime.datetime.now().isoformat()
        logging.info(f"{GREEN_COLOR} {json.dumps(_a_resp)} {RESET_COLOR}")


    except Exception as e:
        _a_resp["error"] = str(e)
        logging.exception(f"ERROR:{str(e)}")

    logging.info( json.dumps(_a_resp, indent=4) )
    return func.HttpResponse(
             json.dumps(_a_resp, indent=4),
             status_code=400
        )