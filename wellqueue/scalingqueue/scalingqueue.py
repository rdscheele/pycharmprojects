import os
import random
import string

from azure.servicebus import ServiceBusService
from kubernetes import client, config
import time

namespace = "default"

bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')

def update_scaling(deployment):
    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        for i in range(0, message_count):
            q = 0  # nyi
    else:
        g = 0  # nyi


if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

deployment = client.V1De()

while True:
    update_scaling(deployment)
    time.sleep(10)
