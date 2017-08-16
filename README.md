# Azure Queue Scale Controller for Kubernetes

This Custom Resource Definition plus controller auto-scales Kubernetes deployments based on the queue length of an Azure Queue.

## Custom Resource Definition

```
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: azurequeues.apex-sample.com
spec:
  group: apex-sample.com
  version: v1
  scope: Namespaced
  names:
    plural: azurequeues
    singular: azurequeue
    kind: AzureQueue
    shortNames:
    - ac
```

## Example Custom Resource

In the custom resource, you must provide the following information.

| AZURESTORAGEACCT | Name of Azure storage account. |
| AZUREQUEUE | Name of Azure Queue. |
| AZUREQUEUEKEY | Access key for the Azure Storage account. |
| QUEUELENGTH | Scale threshold, for every X messages in queue = 1 deployment replica. |
| MIN_REPLICA | Minimum replicas. |
| MAX_REPLICA | Maximum replicas. |
| DEPLOYMENTNAME | Name of deployment to scale. |

```
apiVersion: "apex-sample.com/v1"
kind: AzureQueue
metadata:
  name: process-tweet
spec:
  AZURESTORAGEACCT: kubeazurequeue
  AZUREQUEUE: kubeazurequeue
  AZUREQUEUEKEY:
  QUEUELENGTH: 10
  MIN_REPLICA: 5
  MAX_REPLICA: 20
  DEPLOYMENTNAME: process-tweet
```

## Controller

```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: kube-azure-queue-controller
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: kube-azure-queue-controller
    spec:
      containers:
      - name: kubectl-sidecar
        image: neilpeterson/kubectl-proxy-sidecar
      - name: kube-azure-queue-controller
        image: neilpeterson/azure-queue-controller
```
