FROM python:3
ADD wellprocessor.py /
RUN pip install azure-servicebus
RUN pip install azure-storage
RUN pip install psutil
CMD [ "python", "./wellprocessor.py" ]
