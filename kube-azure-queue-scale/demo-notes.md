# Demo

## Pre-demo
- Run once to download images
- Verify queue is empty
- Verify Cosmos DB is empty

## Load custom resource, controller and deployment
kubectl create -f custom-controller-demo-all-in-one.yaml

## Loop on get pods
while $true; do kubectl get pods; sleep 1; done

## TODO
- Find sutable visualization solution