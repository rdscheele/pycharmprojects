FROM python:3
ADD scalingqueue.py /
RUN pip install azure-servicebus
RUN pip install kubernetes
CMD [ "python", "./scalingqueue.py" ]
