FROM python:3
ADD scalingprocessor.py /
RUN pip install azure-servicebus
RUN pip install azure-storage
CMD [ "python", "./scalingprocessor.py" ]
