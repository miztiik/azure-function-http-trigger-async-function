import os
import logging
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.identity import DefaultAzureCredential
from collections import defaultdict



# EVENT_HUB_FQDN = os.getenv("EVENT_HUB_FQDN", "warehouse-event-hub-ns-event-hub-streams-002.servicebus.windows.net")
# EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME","store-events-stream-002")

# SA_ACCOUNT_URL = os.getenv("SA_ACCOUNT_URL", "https://warehouseodly5v002.blob.core.windows.net/")
# CONTAINER_NAME = os.getenv("CONTAINER_NAME","store-events-blob-002")

# msg_count = 0
# MAX_MESSAGE_COUNT = 10

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
    MAX_MESSAGES_TO_PROCESS = 5
    EVENT_HUB_FQDN = os.getenv("EVENT_HUB_FQDN", "warehouse-event-hub-ns-partition-processor-001.servicebus.windows.net")
    EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME","store-events-stream-001")
    EVENT_HUB_SALE_EVENTS_CONSUMER_GROUP_NAME = os.getenv("EVENT_HUB_SALE_EVENTS_CONSUMER_GROUP_NAME","sale-events-consumers-001")

    CHECKPOINT_COUNT = 10
    partition_recv_cnt_since_last_checkpoint = defaultdict(int)

msg_count = 0

def on_event(partition_context, event):
    # Put your code here.
    # If the operation is i/o intensive, multi-thread will have better performance.
    global msg_count
    msg_count += 1
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print("Received event: {}".format(event.body_as_str()))
    write_or_amend_file(f"Received event: {event.body_as_str()} msg count: {msg_count}\n")
    if msg_count >= GlobalArgs.MAX_MESSAGES_TO_PROCESS:
        partition_context.update_checkpoint(event)
        print("Updated checkpoint at {}".format(event.offset))
        print("Exiting receive handler...")
        raise KeyboardInterrupt("Received {} messages, that's all we need".format(msg_count))
        # os._exit(1)


def write_or_amend_file(content, filename="example.txt"):
    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode) as file:
        file.write(content)

# Write content to the file
write_or_amend_file('Hello, World!\n')

def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))


def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(
        partition_context.partition_id,
        reason
    ))


def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))



def receive_batch(time_limit_seconds=60, message_limit=5):
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
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
        credential=credential,
    )
    try:
        with client:
            client.receive(
                on_event=on_event,
                on_partition_initialize=on_partition_initialize,
                on_partition_close=on_partition_close,
                on_error=on_error,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
    except KeyboardInterrupt:
        print('Stopped receiving.')

receive_batch()
