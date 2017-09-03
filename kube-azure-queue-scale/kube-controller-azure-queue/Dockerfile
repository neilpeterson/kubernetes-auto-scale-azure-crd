FROM python

RUN pip install requests && \
    pip install azure-storage

ADD ./azure-queue-controller.py /app/azure-queue-controller.py

ENTRYPOINT ["python", "/app/azure-queue-controller.py"]

# CMD ["/bin/sh", "-c", "python -u /app/azure-queue-controller.py > kubelog.log 2>&1"]