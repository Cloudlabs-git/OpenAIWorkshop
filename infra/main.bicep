targetScope = 'resourceGroup'
@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string = 'eastus'


param appServicePlanName string = ''
param webServiceName string = ''
// serviceName is used as value for the tag (azd-service-name) azd uses to identify
param serviceName string = 'web'

// Load the abbreviations.json file to use in resource names
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'P2V3'
    }
    kind: 'linux'
    reserved: true
  }
}

// The application frontend
module web './core/host/appservice.bicep' = {
  name: serviceName

  params: {
    name: !empty(webServiceName) ? webServiceName : '${abbrs.webSitesAppService}web-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.10'
    scmDoBuildDuringDeployment: true
    appCommandLine: 'python -m streamlit run multi_agent_copilot.py --server.port 8000 --server.address 0.0.0.0'
    appSettings: {
    AZURE_OPENAI_API_KEY: 'YourOpenAIKey'
    AZURE_OPENAI_ENDPOINT: 'YourOpenAIEndpoint'
    AZURE_OPENAI_EMB_DEPLOYMENT: 'YourOpenAIEMBDeployment'
    AZURE_OPENAI_CHAT_DEPLOYMENT: 'YourOpenAIEMBDeployment' 
    AZURE_OPENAI_EVALUATOR_DEPLOYMENT: 'gpt-4' 

}  
  }
}

// App outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output REACT_APP_WEB_BASE_URL string = web.outputs.uri
