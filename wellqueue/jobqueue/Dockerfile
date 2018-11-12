FROM python:3
ADD jobqueue.py /
RUN pip install azure-servicebus
RUN pip install kubernetes
CMD [ "python", "./jobqueue.py" ]
