FROM python:3
ADD podqueue.py /
RUN pip install azure-servicebus
RUN pip install kubernetes
CMD [ "python", "./podqueue.py" ]
