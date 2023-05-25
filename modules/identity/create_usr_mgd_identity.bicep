param deploymentParams object
param identityParams object
param tags object

// Create User-Assigned Identity
resource r_usr_mgd_identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${identityParams.identityNamePrefix}_${deploymentParams.enterprise_name_suffix}_${deploymentParams.global_uniqueness}'
  location: deploymentParams.location
  tags: tags
}


// Output
output usr_mgd_identity_id string = r_usr_mgd_identity.id
output usr_mgd_identity_clientId string = r_usr_mgd_identity.properties.clientId
output usr_mgd_identity_principalId string = r_usr_mgd_identity.properties.principalId
output usr_mgd_identity_name string = r_usr_mgd_identity.name
