import os
import random
import string
from azure.servicebus import ServiceBusService
from kubernetes import client, config
import time

# TODO: Setting environment variables in cluster. Cleanup this bit really.
namespace = "default"

service_bus_key = open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/service_bus_key.txt', 'r').read()
bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value=service_bus_key)
storage_account_name = 'bbwelldata'
storage_account_key = open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt', 'r').read()

if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

core = client.CoreV1Api()

container_image = "rdscheele/wellprocessor:v20"


# Deconstruct a queue message as list
# Incoming message format is sub-domain;messageId;numberOfMessagesInBatch;fakeCpuValueToBeUsed;fakeMemoryValueToBeUsed
# sub-domain = Name of the blob container in storage
# messageId = Name of the item in the blob container storage
# numberOfMessagesInBatch = The amount of messages that have been send in this batch
# fakeCpuValueToBeUsed = Amount of times Pi is calculated in the well-processor, uses quite a bit of CPU
# fakeMemoryToBeUsed = Size of byte array in the well-processor. Number corresponds to RAM with a max of 800.000.000
def deconstruct_message(msg):
    msg_body = str(msg.body)
    msg_body = msg_body[2:]
    msg_body = msg_body[:-1]
    msg_list = msg_body.split(';')
    container_name = msg_list[0]
    blob_item = msg_list[1]
    cpu_usage = msg_list[3]
    memory_usage = msg_list[4]
    return container_name, blob_item, cpu_usage, memory_usage


# The pod YAML requires you to set a minimum CPU and Memory requirement.
# The incoming message specifies how much memory and CPU the analysis requires.
# This function sets min requirements for memory and min and max requirements for CPU
# TODO: Make this less quick and dirty.
def calculate_required_resources(cpu, memory):
    min_cpu = '0'
    max_cpu = '0'
    if cpu == '2':
        min_cpu = '.1'
        max_cpu = '.2'
    elif cpu == '5':
        min_cpu = '.2'
        max_cpu = '.4'
    elif cpu == '20':
        min_cpu = '.5'
        max_cpu = '1.0'
    min_mem = '0'
    if memory == '100000000':
        min_mem = '150Mi'
    elif memory == '400000000':
        min_mem = '500Mi'
    elif memory == '700000000':
        min_mem = '800Mi'
    return min_cpu, max_cpu, min_mem


# Specify a container that will be used by a pod.
def make_container(msg, pod_id):
    # Get values that are needed to specify the container.
    container_name, blob_item, fake_cpu_usage, fake_memory_usage = deconstruct_message(msg)
    min_cpu, max_cpu, min_mem = calculate_required_resources(fake_cpu_usage, fake_memory_usage)

    # Set the container config specifications
    container = client.V1Container(name="worker")
    container.image = container_image
    container.resources = client.V1ResourceRequirements()
    container.resources.requests = {'cpu': min_cpu, 'memory': min_mem}

    # Set environment variables for the container.
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
    env_var_pod_id = client.V1EnvVar(name='POD_ID')
    env_var_pod_id.value = pod_id
    container.env = [env_var_container_name, env_var_blob_item, env_var_storage_account_name,
                     env_var_storage_account_key, env_var_fake_memory_usage, env_var_fake_cpu_usage, env_var_pod_id]
    return container


# Specify a pod for creation.
def make_pod(msg):
    # Get values from the message
    container_name, blob_item, fake_cpu_usage, fake_memory_usage = deconstruct_message(msg)
    # Created ID for pod
    # TODO: Make ID based on datetime to avoid duplicate ID's
    pod_id = ''.join(random.choices(string.ascii_lowercase, k=20))

    # Set the pod config specifications
    pod = client.V1Job()
    pod.api_version = "v1"
    pod.kind = "Pod"
    pod.metadata = client.V1ObjectMeta()
    pod.metadata.name = 'wellprocessor-' + fake_cpu_usage + '-' + fake_memory_usage + '-' + pod_id
    container = make_container(msg, pod_id)
    pod.spec = client.V1PodSpec(containers=[container])
    pod.spec.restart_policy = "OnFailure"
    pod.spec.termination_grace_period_seconds = 30
    print('Created pod for message ' + str(bus_service.receive_queue_message('wellqueue', peek_lock=True).body) + ' with ID ' + pod_id)
    return pod


def update_queue(msg):
    pod = make_pod(msg)
    core.create_namespaced_pod(namespace, pod)


while True:
    message_count = bus_service.get_queue('wellqueue').message_count

    if message_count != 0:
        # max_cpu, max_ram, curr_cpu, curr_ram = cluster_resources()
        # Get the top most message
        print('Creating a pod!')
        message = bus_service.receive_queue_message('wellqueue', peek_lock=False)
        update_queue(message)

    time.sleep(2)
