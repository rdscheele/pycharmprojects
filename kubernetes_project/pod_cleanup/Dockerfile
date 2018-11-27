FROM python:3
ADD podqueue.py /
RUN pip install kubernetes
CMD [ "python", "./podcleanup.py" ]
