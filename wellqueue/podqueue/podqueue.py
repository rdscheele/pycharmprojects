import os
import random
import string
from azure.servicebus import ServiceBusService
from kubernetes import client, config
import time

namespace = "default"

service_bus_key = open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/service_bus_key.txt', 'r').read()
bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value=service_bus_key)
storage_account_name = 'bbwelldata'
storage_account_key = open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt', 'r').read()


def deconstruct_message():
    # Get the top most message
    msg = bus_service.receive_queue_message('wellqueue', peek_lock=False)

    # Reconstruct the message to be a list
    msg_body = str(msg.body)
    msg_body = msg_body[2:]
    msg_body = msg_body[:-1]
    msg_list = msg_body.split(';')
    container_name = msg_list[0]
    blob_item = msg_list[1]
    return container_name, blob_item


def make_container():
    container = client.V1Container(name="worker")
    container.image = "rdscheele/wellprocessor"
    # Declare required and max resources
    container.resources = client.V1ResourceRequirements()
    container.resources.requests = {'cpu': '0.5', 'memory': '1000Mi'}
    container.resources.limits = {'cpu': '0.7', 'memory': '2000Mi'}
    # Declare environment variables with well id
    container_name, blob_item = deconstruct_message()
    env_var_container_name = client.V1EnvVar(name='CONTAINER_NAME')
    env_var_container_name.value = container_name
    env_var_blob_item = client.V1EnvVar(name='BLOB_ITEM')
    env_var_blob_item.value = blob_item
    env_var_storage_account_name = client.V1EnvVar(name='STORAGE_ACCOUNT_NAME')
    env_var_storage_account_name.value = storage_account_name
    env_var_storage_account_key = client.V1EnvVar(name='STORAGE_ACCOUNT_KEY')
    env_var_storage_account_key.value = storage_account_key
    container.env = [env_var_container_name, env_var_blob_item, env_var_storage_account_name,
                     env_var_storage_account_key]
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
    pod.spec.termination_grace_period_seconds = 30
    return pod


def update_queue(core):
    pod = make_pod()
    core.create_namespaced_pod(namespace, pod)
    print('Created pod for message ' + str(bus_service.receive_queue_message('wellqueue', peek_lock=True).body))


if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()
pod_list = core.list_namespaced_pod(namespace='default')
#print(pod_list)

while True:
    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        update_queue(core)

    pod_list = core.list_namespaced_pod(namespace='default')
    for item in pod_list.items:
        if item.status.phase == 'Succeeded':
            delete_options = client.V1DeleteOptions()
            core.delete_namespaced_pod(name=item.metadata.name, namespace='default', body=delete_options)
            print('Removed terminated pod!')

    time.sleep(10)
