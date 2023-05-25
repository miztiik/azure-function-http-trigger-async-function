# set -x
set -e

# Define colors for console output
GREEN="\e[32m"
RED="\e[31m"
BLUE="\e[34m"
CYAN="\e[36m"
YELLOW="\e[33m"
RESET="\e[0m"
# echo -e "${GREEN}This text is green.${RESET}"


# Set Global Variables
MAIN_BICEP_TEMPL_NAME="main.bicep"
LOCATION=$(jq -r '.parameters.deploymentParams.value.location' params.json)
SUB_DEPLOYMENT_PREFIX=$(jq -r '.parameters.deploymentParams.value.sub_deploymnet_prefix' params.json)
ENTERPRISE_NAME=$(jq -r '.parameters.deploymentParams.value.enterprise_name' params.json)
ENTERPRISE_NAME_SUFFIX=$(jq -r '.parameters.deploymentParams.value.enterprise_name_suffix' params.json)
GLOBAL_UNIQUENESS=$(jq -r '.parameters.deploymentParams.value.global_uniqueness' params.json)

RG_NAME="${ENTERPRISE_NAME}_${ENTERPRISE_NAME_SUFFIX}_${GLOBAL_UNIQUENESS}"
DEPLOYMENT_NAME="${SUB_DEPLOYMENT_PREFIX}_${ENTERPRISE_NAME_SUFFIX}_${GLOBAL_UNIQUENESS}_Deployment"

# # Generate and SSH key pair to pass the public key as parameter
# ssh-keygen -m PEM -t rsa -b 4096 -C '' -f ./miztiik.pem

# pubkeydata=$(cat miztiik.pem.pub)

DEPLOYMENT_OUTPUT_1=""

# Function Deploy all resources
function deploy_everything()
{

echo -e "${YELLOW} Create Resource Group ${RESET}" # Yellow
echo -e "  Initiate RG Deployment: ${CYAN}${RG_NAME}${RESET} at ${CYAN}${LOCATION}${RESET}"
RG_CREATION_OUTPUT=$(az group create -n $RG_NAME --location $LOCATION  | jq -r '.name')

if [ $? == 0 ]; then
    echo -e "${GREEN}   Resource group created successfully. ${RESET}"
else
    echo -e "${RED}   Resource group creation failed. ${RESET}"
    echo -e "${RED}   $RG_CREATION_OUTPUT ${RESET}"
    exit 1
fi


az bicep build --file $1

# Initiate Deployments
echo -e "${YELLOW} Initiate Deployments in RG ${RESET}" # Yellow
echo -e "  Deploy: ${CYAN}${DEPLOYMENT_NAME}${RESET} at ${CYAN}${LOCATION}${RESET}"

az deployment group create \
    --name ${DEPLOYMENT_NAME} \
    --resource-group $RG_NAME \
    --template-file $1 \
    --parameters @params.json


if [ $? == 0 ]; then
    echo -e "${GREEN}  Deployments success. ${RESET}"
else
    echo -e "${RED} Deployments failed. ${RESET}"
    exit 1
fi

}


#########################################################################
#########################################################################
#########################################################################
#########################################################################


deploy_everything $MAIN_BICEP_TEMPL_NAME

