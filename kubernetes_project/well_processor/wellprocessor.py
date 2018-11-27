import os
from azure.storage.blob import BlockBlobService
import time
from decimal import Decimal, getcontext
import psutil

# Get environment variables. These will automatically be set in the YAML by the queue manager.
if os.getenv('KUBERNETES_SERVICE_HOST'):
    # Name of the BLOB container in storage
    container_name = os.environ['CONTAINER_NAME']
    # Name of the item (picture) inside the container
    blob_item = os.environ['BLOB_ITEM']
    # Storage account credentials
    storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
    storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
    # Memory to be used by this container. Integer where each number is one byte, will be byte array.
    # Should never be set higher than 800.000.000 or 800MB
    memory_usage = int(os.environ['FAKE_MEMORY_USAGE'])
    # CPU to be used by this container. Integer where each number is one calculation of pi.
    cpu_usage = int(os.environ['FAKE_CPU_USAGE'])
    # ID (name) of the current pod
    pod_id = os.environ['POD_ID']
else:
    container_name = 'test'
    with open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt', 'r') as myfile:
        storage_account_key = myfile.read()
    storage_account_name = 'bbwelldata'
    blob_item = 'Vlag met geit 9.jpg'
    memory_usage = 400000000
    cpu_usage = 5
    pod_id = 'INVALID'

print('This pod has ID ' + pod_id)

# Connect to blob service
block_blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)

# Find the blob container that this pod has to analyse
blob_list = block_blob_service.list_blobs(container_name)
# Find the item (picture) in the blob container
# There are .sleep() functions in this code to make the analysis take a bit longer.
for item in blob_list:
    blob_name = item.name
    if blob_name == blob_item:
        time.sleep(2)
        # Delete the item from the container
        block_blob_service.delete_blob(container_name=container_name, blob_name=blob_name)
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
        print(psutil.virtual_memory())
        print('Time required to calculate was ' + str(time_diff) + ' seconds for BLOB container item ' + str(blob_item))
        time.sleep(2)
        print(psutil.virtual_memory())
        # Done. Pod should terminate successfully here.
