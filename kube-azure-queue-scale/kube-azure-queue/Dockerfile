FROM python

RUN pip install requests && \
    pip install azure-storage

ADD ./azure-queue-controller.py /app/azure-queue-controller.py

ENTRYPOINT ["python", "/app/azure-queue-controller.py"]