# Event Notified ETL Template App

## What is "Event-Driven"

Event driven architecture is becoming increasingly common in both transactional and analytical processing. According to Martin Fowler, an [Event Driven](https://martinfowler.com/articles/201701-event-driven.html) approach can be typically classified into following:

1. ### Event Notification

Events carry only minimum details, just enough to inform the consumers about a state change. Consumers need to contact the producer to get the new state.

2. ### Event-Carried State Transfer

Events carry the fully copy of the new state. Consumers has enough information to do the processing from the event itself.

3. ### Event-Sourcing

Events are recorded in an event store which then becomes the principal source of the truth. This allows system state to be rebuild by reprocessing the events from events store in the future.

4. ### CQRS

Seperate data models are used for reading and writing information. This can be useful where is single model is too complex for reading and writing data.

## Event Notified ETL

From the perspective of OLAP applications, the two patterns that are most useful are _Event Notification_ and _Event-Carried State Transfer_. Typical stream processing applications such as IOT, real-time telemetry and log analysis systems usually uses the second approach i.e. each event carry a full state. This is quite good if:

1. Fully state can fit in the event pay load, and it can be represented in a structured format.

2. Occurs at regular high frequency intervals.

3. Event sources can be classified in to small number of categories.

However what if the state change is sporadic, content is unstructured or large, and sources are quite varied? For example lets say you are building a system to perform analytics on financial statements or forms of various kinds. Some of these files might be very large and might not confirm to a fixed schema. _Event-Carried State Transfer_ might not be the right choice here and traditional batch process based on regular schedule ETL, polling for state changes and long orchestrated data pipelines might turn out to be inefficient and highly coupled.

Event notified ETL is an excellent alternative in such cases, with following key benefits :

1. Low level of coupling between data sources, data processes and consumers, and therefore better evolvability. It allows you to introduce new sources, consumers and data processing logic without significant changes to the existing ones.

2. Events become natural interfaces and helps break up the long ETL pipelines within the domain boundaries. This helps to reason, build and explain individual pipeline segments with good alignment to these boundaries and reduces the complexity and difficulty in maintaining long chain of ETL pipelines typically associated with traditional batch systems.

### Challenges and solutions

Of course event notification is not panacea for all ETL. A highly decoupled ETL has its benefits, however there are couple of key disadvantages.

1. You might end up with large number of disparate components. This could make application deployment complex and hard to maintain. However this problem can be mitigated to a large extend with a good automation process for deploying application and infrastructure components.

2. It is easy to loose sight of the larger-scale flow. The solution to this problem is to build excellent end to end real-time system monitoring which can provide visibility at higher levels i.e. at the level of event subjects and types.

Native capabilities provided by the major cloud platform makes it relatively easy to implement these solutions. For example, in Azure you can quite easily build deployment automation for required components using ARM templates, Azure CLI and github actions. Same is also true for monitoring; using existing capabilities such as Azure Monitor, Azure Data Explorer, Power BI and Kusto query language it is possible to build end to end flow monitoring with relatively less effort. Other platforms provides similar features e.g. AWS CloudWatch, AWS Kinesis Data Analytics, AWS Quick Sight. This makes event notification especially suitable for building ETL pipelines for modern cloud data platforms.

## Application

This repo contains a sample analytics application which is build using the event notification pattern and can be used as template for getting a better understanding of usefulness and challenges of using this approach for building ETL pipelines. This app also contains It uses NYC Taxi data and is build using Azure Data Platform components.

![Application Architecture](https://github.com/bablulawrence/event-notified-etl/blob/main/design/app-design.svg)

## Application Components

### Azure Event Grid

Azure Event Grid is used for messaging. Following is example of typical an event payload.

```json
[
  {
    "id": "d6d076de-ee09-4e4e-bc78-351f943d8215",
    "subject": "NYCTaxi/GreenTaxi/TripData/green_tripdata_2021-07",
    /*Uniquely identifies the subject of the event, which in this case is the Green Taxi data for July 2021*/
    "eventType": "NYCTaxi.GreenTaxi.TripData.FileCleansed",
    /*Type of the event, which in this case is raised when the Green Taxi data set is cleansed*/
    "data": {
      "folderPath": "/data/cleansed/green_taxi",
      /*Folder path of the cleansed file*/
      "fileName": "green_tripdata_2021-07.csv",
      /*File name of the cleansed file*/
      "uploadedBy": "BabluLawrence@mycompany.com"
    },
    "dataVersion": "1",
    "metadataVersion": "1",
    "eventTime": "2021-12-14T02:20:16.520314",
    "topic": "/subscriptions/fc5bc1f1-a870-4343-a9d3-bb66214af500/resourceGroups/rg-event-etl/providers/Microsoft.EventGrid/topics/eg-topic-gdru573asdpeo"
  }
]
```

### Sharepoint

Two sharepoint sites are used for managing file ingestion.

### Logic Apps

Logic apps are used for event processing.

### Databricks Jobs and Notebooks

Azure Databricks Jobs and Notebooks are used for data processing.

### Azure Data Lake Storage Gen2 and Delta Tables

Azure Data Lake Storage Gen2 and Delta Tables are used for data storage.

## Application Deployment

### Deploy Azure Resources

#### 1. Fork this repo

Fork this repo by clicking the _fork_ button on the top-right of the repository page.

#### 2. Create an Azure Resource Group

Create a resource group for holding Azure resources required for the app. You can do this by running below Azure CLI command in Azure Cloud Shell.

`az group create --location {location} --name {resource group name}`

example :

`az group create --location southeastasia --name rg-event-etl`

#### 3. Create a Service Principal for Azure deployment

Run below command to create a Service Principal scoped to the resource group created in [step 2](#2-create-an-azure-resource-group).

```azurecli
az ad sp create-for-rbac --name "EventEtlSP" \
--role contributor \
--scopes /subscriptions/{subscription id}/resourceGroups/{resource group name}
```

example :

```azurecli
az ad sp create-for-rbac --name "EventEtlSP" \
--role contributor \
--scopes /subscriptions/1ee5ed92-933d-4c51-ac9f-96329a4273f7/resourceGroups/rg-event-etl
```

output will be like :

```azurecli
{
    "clientId": "<GUID>",
    "clientSecret": "<GUID>",
    "subscriptionId": "<GUID>",
    "tenantId": "<GUID>",
    (...)
}
```

hold on to this, you will need in the next step.

#### 4. Add Github Secrets

Create the following secrets variables under your repository - _Settings -> Secrets_. The secret names should match exactly what is given below.

| #   | Secret Name       | Description                                                                                                      |
| --- | ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | AZURE_CREDENTIALS | Service Principal Details for deployment, [output of step 3](#3-create-a-service-principal-for-azure-deployment) |

#### 5. Run Github workflow

Under `Actions` in your forked repository, you will find following workflows. Run them manually by clicking _workflow name -> run workflow_, in the sequence given below.

| #   | Workflow         | Description                                | Sequence  | Triggers |
| --- | ---------------- | ------------------------------------------ | --------- | -------- |
| 1   | Deploy Resources | Provisions application components in Azure | run first | Manual   |

### 6. Logic app connection authentication

Login to Azure Portal and authenticate following logic app connections.

| #   | Connection            | Description                                            | Authentication Type                |
| --- | --------------------- | ------------------------------------------------------ | ---------------------------------- |
| 1   | sharepointonline      | Connection to SharePoint read data                     | OAuth 2.0 Authorization Code Grant |
| 2   | azureeventgrid        | Connection consume events from Azure Event Grid        | OAuth 2.0 Authorization Code Grant |
| 3   | azureeventgridpublish | Connection to publish events to Azure Event Grid       | SAS Key                            |
| 4   | azureblob             | Connection to Azure Data Lake Gen2 read and write data | Managed Identity                   |
| 5   | powerbi               | Connection to refresh PowerBI Datasets                 | OAuth 2.0 Authorization Code Grant |

### 7. Give Storage Account access to Logic apps

Assign RBAC role `Storage Data Contributor` to manage identity of the Logic app `logic-app-raw-file-uploaded` by running following Azure CLI commands

```azurecli

servicePrincipalId=$(az resource list -g <Resource Group Name> -n 'logic-app-raw-file-uploaded' --query [*].identity.principalId --out tsv)

az role assignment create \
    --assignee $servicePrincipalId \
    --role 'Storage Blob Data Contributor' \
    --scope /subscriptions/<Subscription Id>/resourceGroups/rg-event-etl/providers/Microsoft.Storage/storageAccounts/<Storage Account Name>

```

### 8. Mount ADLS Gen2 in Databricks

1. Create an Azure AD app and client secret. Note the object id of the Service Principal(Enterprise Application)

2. Assign RBAC role `Storage Data Contributor` to Databricks workspace by running following Azure CLI commands

```azurecli

az role assignment create \
    --assignee <Service Principal Object Id> \
    --role 'Storage Blob Data Contributor' \
    --scope /subscriptions/<Subscription Id>/resourceGroups/rg-event-etl/providers/Microsoft.Storage/storageAccounts/<Storage Account Name>

```

3. Create databricks scope and store the client secret value in it using the following commands

   ```bash
   databricks secrets create-scope --scope datalake
   databricks secrets put --scope datalake --key adappsecret

   ```

4. Open the notebook `nb-01-setup.py` in the Databricks workspace and update the `clientId`, `scope`, `key`, `storageAccountName` and with the values from step 2. Run the notebook to mount the data lake directory in Databricks

### 9. Publish PowerBI datasets and reports

1. Open the PBIX file from folder `/powerbi` using Power BI Desktop. Update the following setting in the data set connection from the databricks workspace created in

   1. Databricks workspace URI
   2. Cluster Id
   3. Personal Access Token

2. Login to Power BI service and publish the PBIX file to your workspace.

### 10. SharePoint Setup

Create Two SharePont Online Team Sites - Green Taxi and Yellow Taxi and create following folders to upload taxi data

- Green Taxi - `Documents/monthly`
- Yellow Taxi - `Documents/daily`

You will the data to upload in /data folder of this repo.

Note: You can sign up for Office 365 E3 license if you don't have access to a SharePoint Online subscription.

### 11. Power Automate Setup

Login to Power Automate and create connection to SharePoint and Azure Event Grid. Once the connections are setup, import the flows to publish the events from `/power_automate` folder of the repo.

## Running the application

1. Upload the Green Taxi data files to the SharePoint site. Following series of events will be raised as the workflows are executed.

   1. `NYCTaxi.GreenTaxi.TripData.FileIngested`
   2. `NYCTaxi.GreenTaxi.TripData.RawFileUploaded`
   3. `NYCTaxi.GreenTaxi.TripData.ProcessRawStarted`
   4. `NYCTaxi.GreenTaxi.TripData.FileCleansed`
   5. `NYCTaxi.GreenTaxi.TripData.ProcessCleansedStarted`
   6. `NYCTaxi.GreenTaxi.TripData.ZoneSummaryCurated`
   7. `NYCTaxi.GreenTaxi.TripData.ZoneSummaryDataRefreshed`

   If any of the steps fail, an error event with suffix `.Failed` e.g. `NYCTaxi.GreenTaxi.TripData.FileCleansed.Failed` will be generated. Similar events will be generated when repeat the process for Yellow Taxi data.

2. Execute the job `jb-04-zone-lookup-process-all`. This will load the NYC Zone Lookup data and create the necessary hive tables for data consumption.

3. Run the sample queries in notebook `nb-05-nyc-taxi-validate` to check the data.

4. Login to the Power BI and run the nyc-taxi reports to explore the Total Passenger Count By Borough, Zone and Taxi Type.

## References

1. https://martinfowler.com/articles/201701-event-driven.html2
2. https://docs.microsoft.com/en-us/azure/event-grid/overview
3. https://www.microsoft.com/en-in/microsoft-365/enterprise/office-365-e3?activetab=pivot%3aoverviewtab
4. https://docs.microsoft.com/en-us/power-automate/import-flow-solution
5. https://docs.microsoft.com/en-us/power-automate/add-manage-connections
6. https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
