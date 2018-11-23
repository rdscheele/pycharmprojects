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

fake_memory_usage = 500000
fake_cpu_usage = 10

if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()


# Deconstruct a queue message as list
def deconstruct_message(msg):
    msg_body = str(msg.body)
    msg_body = msg_body[2:]
    msg_body = msg_body[:-1]
    msg_list = msg_body.split(';')
    container_name = msg_list[0]
    blob_item = msg_list[1]
    return container_name, blob_item


def make_container(msg):
    container = client.V1Container(name="worker")
    container.image = "rdscheele/wellprocessor"
    # Declare required and max resources
    container.resources = client.V1ResourceRequirements()
    #container.resources.requests = {'cpu': '0.5', 'memory': '1000Mi'}
    #container.resources.limits = {'cpu': '0.7', 'memory': '2000Mi'}
    # Declare environment variables with well id
    container_name, blob_item = deconstruct_message(msg)
    env_var_container_name = client.V1EnvVar(name='CONTAINER_NAME')
    env_var_container_name.value = container_name
    env_var_blob_item = client.V1EnvVar(name='BLOB_ITEM')
    env_var_blob_item.value = blob_item
    env_var_storage_account_name = client.V1EnvVar(name='STORAGE_ACCOUNT_NAME')
    env_var_storage_account_name.value = storage_account_name
    env_var_storage_account_key = client.V1EnvVar(name='STORAGE_ACCOUNT_KEY')
    env_var_storage_account_key.value = storage_account_key
    env_var_fake_memory_usage = client.V1EnvVar(name='FAKE_MEMORY_USAGE')
    env_var_fake_memory_usage.value = fake_memory_usage
    env_var_fake_cpu_usage = client.V1EnvVar(name='FAKE_CPU_USAGE')
    env_var_fake_cpu_usage.value = fake_cpu_usage
    container.env = [env_var_container_name, env_var_blob_item, env_var_storage_account_name,
                     env_var_storage_account_key]
    return container


def make_pod(msg):
    pod = client.V1Job()
    pod.api_version = "v1"
    pod.kind = "Pod"
    pod.metadata = client.V1ObjectMeta()
    pod.metadata.name = 'pod-wellprocessor-'.join(random.choices(string.ascii_lowercase, k=8))
    container = make_container(msg)
    pod.spec = client.V1PodSpec(containers=[container])
    pod.spec.restart_policy = "Never"
    pod.spec.termination_grace_period_seconds = 30
    return pod


def update_queue(msg):
    pod = make_pod(msg)
    core.create_namespaced_pod(namespace, pod)
    print('Created pod for message ' + str(bus_service.receive_queue_message('wellqueue', peek_lock=True).body))


def cluster_resources():
    pod_list = core.list_namespaced_pod(namespace='default')
    node_list = core.list_node()
    current_cpu = 0
    current_cpu = 0
    maximum_cpu = 0
    maximum_ram = 0

    return maximum_cpu, maximum_ram, current_cpu, current_cpu


while True:
    # Cleanup completed pods
    pod_list = core.list_namespaced_pod(namespace='default')
    for item in pod_list.items:
        if item.status.phase == 'Succeeded':
            delete_options = client.V1DeleteOptions()
            #core.delete_namespaced_pod(name=item.metadata.name, namespace='default', body=delete_options)
            print('Removed terminated pod!')

    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        max_cpu, max_ram, curr_cpu, curr_ram = cluster_resources()
        # Get the top most message
        message = bus_service.receive_queue_message('wellqueue', peek_lock=False)
        update_queue(message)



    time.sleep(10)
