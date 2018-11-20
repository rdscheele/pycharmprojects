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


def make_container():
    container = client.V1Container(name="worker")
    container.image = "rdscheele/wellprocessor"
    return container


def make_pod():
    pod = client.V1Job()
    pod.api_version = "v1"
    pod.kind = "Pod"
    pod.metadata = client.V1ObjectMeta()
    pod.metadata.name = 'pod-wellprocessor-'.join(random.choices(string.ascii_lowercase, k=8))
    container = make_container()
    pod.spec = client.V1PodSpec(containers=[container])
    pod.spec.restart_policy = "Never"

    return pod


def update_queue(core):
    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        for i in range(0, message_count):
            pod = make_pod()
            core.create_namespaced_pod(namespace, pod)
            print('Created pod')
            time.sleep(60)


if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()

config_map = core.list_namespaced_config_map(namespace='default')
print(config_map)
#while True:
#update_queue(core)
#time.sleep(10)
