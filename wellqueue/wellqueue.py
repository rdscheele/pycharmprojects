import os
from azure.servicebus import ServiceBusService
from kubernetes import client, config
import time

namespace = "default"

bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')


def make_container():
    container = client.V1Container()
    container.image = "rdscheele/wellprocessor:v2"
    container.name = "worker"
    return container


def make_job():
    job = client.V1Job()
    job.metadata = client.V1ObjectMeta()
    job.spec = client.V1JobSpec()
    job.spec.template = client.V1PodTemplate()
    job.spec.template.spec = client.V1PodTemplateSpec()
    job.spec.template.spec.restart_policy = "Never"
    job.spec.template.spec.containers = [
        make_container()
    ]
    return job


def update_queue(batch):
    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        for i in range(0, message_count):
            job = make_job()
            batch.create_namespaced_job(namespace, job)
            print('Created job')
            time.sleep(60)


if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

batch = client.BatchV1Api()

while True:
    update_queue(batch)
    time.sleep(10)
