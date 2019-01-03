import os
from azure.storage.blob import BlockBlobService
import time
from decimal import Decimal, getcontext
import psutil
from azure.servicebus import ServiceBusService


"""
The piece of code below makes this container do something. It is just an example.
It has no practical use at all.
If this code is ran in the k8s cluster as a container, some resources (memory and CPU) will be reserved for this 
specific container. It will have status 'Running' when it is being executed.
If the container has done it's job and the status changes to 'Succeeded' or 'Completed' the resources will be free
once again.
"""


# Set environment variables if the environment this code is ran in is a k8s environment.
if os.getenv('KUBERNETES_SERVICE_HOST'):
    # Name of the BLOB container in storage
    container_name = os.environ['CONTAINER_NAME']
    # Name of the item (picture) inside the container
    blob_item = os.environ['BLOB_ITEM']
    # Storage account credentials
    storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
    storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
    # Memory to be used by this container. Integer where each number is one byte, will be byte array.
    # Should never be set higher than 800.000.000 or 800MB (In this specific example -> the byte array will overflow)
    memory_usage = int(os.environ['FAKE_MEMORY_USAGE'])
    # CPU to be used by this container. Integer where each number is one calculation of pi.
    cpu_usage = int(os.environ['FAKE_CPU_USAGE'])
    # ID (name) of the current pod
    pod_id = os.environ['POD_ID']
    # Service bus credentials
    service_bus_key = os.environ['SERVICE_BUS_KEY']
    service_bus_namespace = os.environ['SERVICE_BUS_NAMESPACE']
# Set environment variables if the environment this code is ran in is NOT a k8s environment. (Ran locally)
else:
    container_name = 'test'
    with open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt', 'r') as myfile:
        storage_account_key = myfile.read()
    storage_account_name = 'bbwelldata'
    blob_item = 'Vlag met geit 9.jpg'
    memory_usage = 400000000
    cpu_usage = 5
    pod_id = 'INVALID'
    service_bus_key = open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/service_bus_key.txt', 'r').read()
    service_bus_namespace = 'wellprototype'

# Create the service bus service
bus_service = ServiceBusService(
    service_namespace=service_bus_namespace,
    shared_access_key_name='master',
    shared_access_key_value=service_bus_key)

print('This pod has ID ' + pod_id)

# Connect to blob service
block_blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)


# Remove the message from the active queue
def remove_message(msg_blob_name):
    q = 0
    run = True
    while run:
        q = q + 1
        message = bus_service.receive_queue_message(queue_name='activequeue', peek_lock=True)
        msg_blob_item = deconstruct_message(message)
        if msg_blob_item == msg_blob_name:
            message.delete()
            run = False
        if q > 5000:
            run = False
            print('Something really strange happened, getting this error is practically impossible.')


# Get the message item name
def deconstruct_message(msg):
    msg_body = str(msg.body)
    msg_body = msg_body[2:]
    msg_body = msg_body[:-1]
    msg_list = msg_body.split(';')
    blob_item_msg = msg_list[1]
    return blob_item_msg


# Find the blob container that this pod has to analyse
blob_list = block_blob_service.list_blobs(container_name)
# Find the item (picture) in the blob container
# There are .sleep() functions in this code to make the analysis take a bit longer.
for item in blob_list:
    blob_name = item.name
    if blob_name == blob_item:
        time.sleep(2)
        print(psutil.virtual_memory())
        time.sleep(2)
        time_start = time.time()
        pi = 0
        for i in range(0, cpu_usage):
            # Create byte array which can consume RAM
            a = bytearray(memory_usage)
            getcontext().prec = 100
            # Calculate PI
            pi = sum(1 / Decimal(16) ** k *
                     (Decimal(4) / (8 * k + 1) -
                      Decimal(2) / (8 * k + 4) -
                      Decimal(1) / (8 * k + 5) -
                      Decimal(1) / (8 * k + 6)) for k in range(500000))
            time.sleep(2)
        print('Pi is calculated to be ' + str(pi) + ' ')
        time_end = time.time()
        time_diff = time_end - time_start
        time.sleep(2)
        print('Removing message from active queue')
        # Remove message from activequeue
        remove_message(blob_name)
        time.sleep(2)
        print('Time required to run this container was ' + str(time_diff) + ' seconds for BLOB container item '
              + str(blob_item))
        time.sleep(600)
        # Delete the item from the container
        print('Container name ' + container_name)
        print('Blob name ' + blob_name)
        block_blob_service.delete_blob(container_name=container_name, blob_name=blob_name)
        time.sleep(2)
        print(psutil.virtual_memory())
        # Done. Pod should have terminated successfully here with status 'Succeeded' or 'Completed'.
        # The resources that were specified as 'min CPU' and 'min memory' should be free in the cluster again.
