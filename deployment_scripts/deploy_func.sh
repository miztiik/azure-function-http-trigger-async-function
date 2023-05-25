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


# Publish the function App
function deploy_func_code(){

    FUNC_APP_NAME_PART_1=$(jq -r '.parameters.deploymentParams.value.enterprise_name_suffix' params.json)
    FUNC_APP_NAME_PART_2=$(jq -r '.parameters.funcParams.value.funcAppPrefix' params.json)
    FUNC_APP_NAME_PART_3="fn-app"
    GLOBAL_UNIQUENESS=$(jq -r '.parameters.deploymentParams.value.global_uniqueness' params.json)
    FUNC_APP_NAME=${FUNC_APP_NAME_PART_1}-${FUNC_APP_NAME_PART_2}-${FUNC_APP_NAME_PART_3}-${GLOBAL_UNIQUENESS}
    FUNC_APP_NAME="${FUNC_APP_NAME//_/-}"
    # echo "$FUNC_APP_NAME"

    FUNC_CODE_LOCATION="./app/function_code/store-backend-ops/"

    pushd ${FUNC_CODE_LOCATION}

    # Initiate Deployments
    echo -e "${YELLOW} Initiating Python Function Deployment ${RESET}" # Yellow
    echo -e "  Deploying code from ${CYAN}${FUNC_CODE_LOCATION}${RESET} to ${CYAN}${FUNC_APP_NAME}${RESET} \033[0m" # Green

    func azure functionapp publish ${FUNC_APP_NAME} --nozip
    popd
}




#########################################################################
#########################################################################
#########################################################################
#########################################################################


deploy_func_code
