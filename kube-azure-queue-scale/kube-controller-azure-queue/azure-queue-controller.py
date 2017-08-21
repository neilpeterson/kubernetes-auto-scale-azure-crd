from azure.storage.queue import QueueService
import json
import math
import os
import requests
import sys
import time

CUSTOM_RESOURCE_DEF = "http://localhost:8001/apis/apex-sample.com/v1/namespaces/default/azurequeues"

while True:    
    
    # Instantiate KUBERNETES_API Custom Resource Definition (CRD) object. 
    try:
        RESPONSE = requests.get(CUSTOM_RESOURCE_DEF)
    except requests.exceptions.RequestException as e:
        print('Could not connect to: ' + CUSTOM_RESOURCE_DEF + ' API. Program will exit.')
        sys.exit(1)

    if RESPONSE.status_code != 200:
        print("Could not find Azure Queue resource definition: " + CUSTOM_RESOURCE_DEF)
    else:
        object = json.loads(RESPONSE.text)
        
        # Check for CRD instance (custom resource).
        if not object['items']:
            print("No Azure Queue custom resources found.")

        # Loop through each CRD instance.
        for item in object['items']:

            # Parse values from CRD instance.
            AZURE_QUEUE = item['spec']['AZUREQUEUE']
            AZURE_QUEUE_KEY = item['spec']['AZUREQUEUEKEY']
            AZURE_STORAGE_ACCT = item['spec']['AZURESTORAGEACCT']
            DEPLOYMENT_NAME = item['spec']['DEPLOYMENTNAME']
            QUEUE_LENGTH = item['spec']['QUEUELENGTH']
            MIN_REPLICA = item['spec']['MIN_REPLICA']
            MAX_REPLICA = item['spec']['MAX_REPLICA']             

            # Build deployment API location based on deployment name collected from CRD instance.
            DEPLOYMENT = "http://localhost:8001/apis/extensions/v1beta1/namespaces/default/deployments/" + DEPLOYMENT_NAME + "/scale"

            # Build Azure queue object based on Azure Storage name and key collected from CRD instance.
            queue_service = QueueService(account_name=AZURE_STORAGE_ACCT, account_key=AZURE_QUEUE_KEY)
            
            # Get queue length from Azure Queue
            metadata = queue_service.get_queue_metadata(AZURE_QUEUE)
            queue_length = metadata.approximate_message_count

            # Catch error in the event the K8S API is no longer accessible.
            try:
                r = requests.get(DEPLOYMENT)
            except requests.exceptions.RequestException as e:
                print('Could not connect to: ' + KUBERNETES_API + ' API. Program will exit.')
                sys.exit(1)
            
            # Log if deployment to scale is not found.
            # Get current deployment count.
            if r.status_code != 200:
                print('Could not find deployment: ' + DEPLOYMENT_NAME)
            else:
                s = json.loads(r.text)
                replica_count = (s['status']['replicas'])

                # Determine how many replicas are required.
                needed_replicas = math.ceil(queue_length/int(QUEUE_LENGTH))
                
                # Ensure min and max replica values are being used (quick hack).
                if needed_replicas < MIN_REPLICA:
                    needed_replicas = MIN_REPLICA
                elif needed_replicas > MAX_REPLICA:
                    needed_replicas = MAX_REPLICA

                # Calculate replicas to start / stop (output only).
                start_replicas = math.ceil(needed_replicas - replica_count)

                # Main output for scale operations.
                print('K8S Deployment: ' + DEPLOYMENT_NAME + ' -- Queue Length: ' + str(queue_length) + ' -- Queue Max: ' + str(QUEUE_LENGTH) + ' -- Current Replicas: ' + str(replica_count) + ' -- Needed Replicas: ' + str(needed_replicas) + ' -- To Start: ' + str(start_replicas))

                # If needed, change replica count on deployment.
                if (needed_replicas) != replica_count:                            
                    s['spec']['replicas'] = needed_replicas
                    e = json.dumps(s)
                    z = requests.put(DEPLOYMENT, data=e)