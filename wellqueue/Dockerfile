FROM python:3
ADD queue.py /
RUN pip install azure-servicebus
RUN pip install kubernetes
CMD [ "python", "./queue.py" ]
