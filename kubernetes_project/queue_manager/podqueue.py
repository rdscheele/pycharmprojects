import os
import random
import string
from azure.servicebus import ServiceBusService
from kubernetes import client, config
import time
import datetime


""" 
This function is the so called 'manager'.
It can be ran locally or as a deployment inside a k8s cluster.
"""


# Variables
namespace = "default"
service_bus_key_lcation = 'C:/Users/r.d.scheele/OneDrive - Betabit/Keys/service_bus_key.txt'
service_bus_namespace = 'wellprototype'
storage_account_name = 'bbwelldata'
storage_account_key_lcation = 'C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt'
# The image I am using for my containers. If you have build your own docker image it should be changed.
# If not just leave it.
container_image = "rdscheele/wellprocessor:v25"


# Service bus variables.
service_bus_key = open(service_bus_key_lcation, 'r').read()
bus_service = ServiceBusService(
    service_namespace=service_bus_namespace,
    shared_access_key_name='master',
    shared_access_key_value=service_bus_key)

# Storage account variables.
storage_account_key = open(storage_account_key_lcation, 'r').read()

# If ran outside of the k8s cluster, load config from outside the cluster.
# Requires Azure CLI. Make sure you've ran 'az aks get-credentials' for your cluster.
# If ran inside k8s cluster, just load config from inside the cluster.
if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

# Load the API functions.
core = client.CoreV1Api()


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
    # Returns single variables for items in the message.
    return container_name, blob_item, cpu_usage, memory_usage


# The container requires you to set a minimum CPU and Memory requirement.
# The incoming message specifies how much memory and CPU the message requires.
# The min_mem and min_cpu should be the minimum required resources the analysis requires.
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
        min_mem = '125Mi'
    elif memory == '400000000':
        min_mem = '425Mi'
    elif memory == '700000000':
        min_mem = '725Mi'
    return min_cpu, max_cpu, min_mem


# Specify a container that will be used by a pod.
def make_container(msg, pod_id):
    # Get values from the message for the container.
    container_name, blob_item, fake_cpu_usage, fake_memory_usage = deconstruct_message(msg)
    # Calculate the resource requirements for this message.
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
    env_var_service_bus_namespace = client.V1EnvVar(name='SERVICE_BUS_NAMESPACE')
    env_var_service_bus_namespace.value = service_bus_namespace
    env_var_service_bus_key = client.V1EnvVar(name='SERVICE_BUS_KEY')
    env_var_service_bus_key.value = service_bus_key
    container.env = [env_var_container_name, env_var_blob_item, env_var_storage_account_name,
                     env_var_storage_account_key, env_var_fake_memory_usage, env_var_fake_cpu_usage, env_var_pod_id,
                     env_var_service_bus_key, env_var_service_bus_namespace]
    return container


# Specify a pod for creation.
def make_pod(msg):
    # Get values from the message
    container_name, blob_item, fake_cpu_usage, fake_memory_usage = deconstruct_message(msg)
    # Created ID for pod
    # TODO: Make ID based on datetime to avoid duplicate ID's.
    # NOTE: If k8s receives a pod with a name that already exists the pod won't be scheduled.
    pod_id = ''.join(random.choices(string.ascii_lowercase, k=20))

    # Set the pod config specifications
    pod = client.V1Job()
    pod.api_version = "v1"
    pod.kind = "Pod"
    pod.metadata = client.V1ObjectMeta()
    pod.metadata.name = fake_memory_usage + '-wellprocessor-' + fake_cpu_usage + '-' + pod_id
    # Create and declare the container that is going to be used.
    container = make_container(msg, pod_id)
    pod.spec = client.V1PodSpec(containers=[container])
    # Set a restart policy.
    # NOTE: These pods will infinitely restart on failure, it is probably better to set a max restarts.
    pod.spec.restart_policy = "OnFailure"
    pod.spec.termination_grace_period_seconds = 30
    print('Created pod for message ' + str(msg.body) + ' with ID ' + pod_id)
    return pod


# Read the message from the service bus queue. Send message to new service bus queue.
def read_message():
    message = bus_service.receive_queue_message(queue_name='wellqueue', peek_lock=False)
    bus_service.send_queue_message(queue_name='activequeue', message=message)
    return message


# This is called when a new pod can be created.
def update_queue():
    msg = read_message()
    pod = make_pod(msg)
    core.create_namespaced_pod(namespace, pod)


# Check if there are any pods with status 'pending'.
def check_pending_pods():
    pod_list = core.list_pod_for_all_namespaces().items
    for item in pod_list:
        if item.status.phase == 'Pending':
            return True
    return False


start_time = datetime.datetime.now()

# The loop that this function wil run.
while True:
    # See if there are pods with 'pending' status in the queue currently.
    pending = check_pending_pods()

    if not pending:
        # Check if there are messages in the service bus queue.
        message_count = bus_service.get_queue('wellqueue').message_count
        if message_count != 0:
            new_time = datetime.datetime.now()
            time_difference = new_time - start_time
            start_time = datetime.datetime.now()
            print('Creating pod. Timediff between now and previous pod is ' + str(time_difference) + ' seconds.')
            update_queue()
        else:
            time.sleep(20)

    time.sleep(1)
