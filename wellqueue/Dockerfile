FROM python:3
ADD wellqueue.py /
RUN pip install azure-servicebus
RUN pip install kubernetes
CMD [ "python", "./wellqueue.py" ]
