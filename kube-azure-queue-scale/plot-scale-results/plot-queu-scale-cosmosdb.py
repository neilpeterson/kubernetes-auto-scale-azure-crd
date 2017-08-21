from azure.storage.queue import QueueService
import pydocumentdb
import pydocumentdb.document_client as document_client
import json
import os
import requests
import time

# Azure storage
AZURE_QUEUE = os.environ['AZURE_QUEUE']
AZURE_QUEUE_KEY = os.environ['AZURE_QUEUE_KEY']
AZURE_STORAGE_ACCT = os.environ['AZURE_STORAGE_ACCT']
queue_service = QueueService(account_name=AZURE_STORAGE_ACCT, account_key=AZURE_QUEUE_KEY) 

# Kubernetes API
DEPLOYMENT_NAME = os.environ['DEPLOYMENT_NAME']
DEPLOYMENT = "http://localhost:8001/apis/extensions/v1beta1/namespaces/default/deployments/" + DEPLOYMENT_NAME + "/scale"

# Cosmos DB
COSMOS_DB_ENDPOINT = os.environ['COSMOS_DB_ENDPOINT']
COSMOS_DB_MASTERKEY = os.environ['COSMOS_DB_MASTERKEY']
COSMOS_DB_DATABASE = os.environ['COSMOS_DB_DATABASE']
COSMOS_DB_COLLECTION = os.environ['COSMOS_DB_COLLECTION']
client = document_client.DocumentClient(COSMOS_DB_ENDPOINT, {'masterKey': COSMOS_DB_MASTERKEY})

############# Start Functions

# Initialize Cosmos DB
def cosmosdb():

    # Check for database
    try:
        db = next((data for data in client.ReadDatabases() if data['id'] == COSMOS_DB_DATABASE))
    # Create if missing
    except:
        db = client.CreateDatabase({'id': COSMOS_DB_DATABASE})

    # Check for collection
    try:
        collection = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == COSMOS_DB_COLLECTION))
    # Create if missing
    except:
        options = {
            'offerEnableRUPerMinuteThroughput': True,
            'offerVersion': "V2",
            'offerThroughput': 400
        }

        # Create a collection
        collection = client.CreateCollection(db['_self'], {'id': COSMOS_DB_COLLECTION}, options)

    # Return collection
    return collection

# Add queue length and replica count to Cosmos DB
def add_value_cosmosdb(queue_length,replica_count):
    client.CreateDocument(collection['_self'],
        {
            'queue_length': queue_length,
            'replica_count': replica_count
        })

############# End Functions

# Initalize Cosmos DB
collection = cosmosdb()

# Plot queue length and replica count
while True:

    # Get queue length
    metadata = queue_service.get_queue_metadata(AZURE_QUEUE)
    queue_length = metadata.approximate_message_count

    # Catch error in the event the K8S API is no longer accessible.
    try:
        r = requests.get(DEPLOYMENT)
    except requests.exceptions.RequestException as e:
        print('Could not connect to: ' + KUBERNETES_API + ' API. Program will exit.')
        sys.exit(1)

    # Get Kubernetes deployment replica count
    if r.status_code != 200:
        print('Could not find deployment: ' + DEPLOYMENT_NAME)
    else:
        s = json.loads(r.text)
        replica_count = (s['status']['replicas'])

        print(queue_length)
        print(replica_count)

        add_value_cosmosdb(queue_length,replica_count)

    time.sleep(1)