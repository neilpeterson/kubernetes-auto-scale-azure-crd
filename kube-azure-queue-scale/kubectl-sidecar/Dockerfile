FROM ubuntu

RUN apt-get update && \ 
    apt-get install curl -y

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.7.0/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl

ENTRYPOINT ["/usr/local/bin/kubectl", "proxy"]