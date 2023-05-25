// targetScope = 'subscription'

targetScope = 'resourceGroup'

// Parameters
param deploymentParams object
param identityParams object

param storageAccountParams object
param logAnalyticsWorkspaceParams object
param funcParams object

param brandTags object

param dateNow string = utcNow('yyyy-MM-dd-hh-mm')

param tags object = union(brandTags, {last_deployed:dateNow})


// Create Identity
module r_usr_mgd_identity 'modules/identity/create_usr_mgd_identity.bicep' = {
  name: '${deploymentParams.enterprise_name_suffix}_${deploymentParams.global_uniqueness}_usr_mgd_identity'
  params: {
    deploymentParams:deploymentParams
    identityParams:identityParams
    tags: tags
  }
}

// Create the Log Analytics Workspace
module r_logAnalyticsWorkspace 'modules/monitor/log_analytics_workspace.bicep' = {
  name: '${logAnalyticsWorkspaceParams.workspaceName}_${deploymentParams.global_uniqueness}_la'
  params: {
    deploymentParams:deploymentParams
    logAnalyticsWorkspaceParams: logAnalyticsWorkspaceParams
    tags: tags
  }
}


// Create Storage Account
module r_sa 'modules/storage/create_storage_account.bicep' = {
  name: '${storageAccountParams.storageAccountNamePrefix}_${deploymentParams.global_uniqueness}_sa'
  params: {
    deploymentParams:deploymentParams
    storageAccountParams:storageAccountParams
    funcParams: funcParams
    tags: tags
  }
}


// Create Storage Account - Blob container
module r_blob 'modules/storage/create_blob.bicep' = {
  name: '${storageAccountParams.storageAccountNamePrefix}_${deploymentParams.global_uniqueness}_blob'
  params: {
    deploymentParams:deploymentParams
    storageAccountParams:storageAccountParams
    storageAccountName: r_sa.outputs.saName
    storageAccountName_1: r_sa.outputs.saName_1
    logAnalyticsWorkspaceId: r_logAnalyticsWorkspace.outputs.logAnalyticsPayGWorkspaceId
    enableDiagnostics: false
  }
  dependsOn: [
    r_sa
    r_logAnalyticsWorkspace
  ]
}

// Create the function app & Functions
module r_fn_app 'modules/functions/create_function.bicep' = {
  name: '${funcParams.funcNamePrefix}_${deploymentParams.global_uniqueness}_fn_app'
  params: {
    deploymentParams:deploymentParams
    r_usr_mgd_identity_name: r_usr_mgd_identity.outputs.usr_mgd_identity_name
    funcParams: funcParams
    funcSaName: r_sa.outputs.saName_1

    logAnalyticsWorkspaceId: r_logAnalyticsWorkspace.outputs.logAnalyticsPayGWorkspaceId
    enableDiagnostics: true
    tags: tags

    saName: r_sa.outputs.saName
    blobContainerName: r_blob.outputs.blobContainerName
  }
  dependsOn: [
    r_sa
    r_logAnalyticsWorkspace
  ]
}

