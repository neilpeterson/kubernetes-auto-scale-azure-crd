from kubernetes import client, config

client.Configuration().host="http://localhost:8001"

# Initial test - works
# v1 = client.CoreV1Api()
# print(dir(v1))

# CRD - does not work
# crd = client.CustomObjectsApi()
# resp = crd.get_cluster_custom_object("apex-sample.com", "v1", "azurequeues", "azurequeues.apex-sample.com")
# print(resp)

# Deployment
deployment = client.ExtensionsV1beta1Api()
resp = deployment.list_deployment_for_all_namespaces(label_selector="app", watch=watch)
# print(resp)

for item in resp.items:
    print(item.status.replicas)