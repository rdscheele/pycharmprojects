import os
from azure.storage.blob import BlockBlobService
import time
from decimal import Decimal, getcontext
import psutil

if os.getenv('KUBERNETES_SERVICE_HOST'):
    container_name = os.environ['CONTAINER_NAME']
    blob_item = os.environ['BLOB_ITEM']
    storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
    storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
    memory_usage = int(os.environ['FAKE_MEMORY_USAGE'])
    cpu_usage = int(os.environ['FAKE_CPU_USAGE'])
    pod_id = os.environ['POD_ID']
else:
    container_name = 'test'
    with open('C:/Users/r.d.scheele/OneDrive - Betabit/Keys/storage_account_key.txt', 'r') as myfile:
        storage_account_key = myfile.read()
    storage_account_name = 'bbwelldata'
    blob_item = 'vlag_met_geit.jpg'
    memory_usage = 400000000
    cpu_usage = 10
    pod_id = 'INVALID'

print('This pod has ID ' + pod_id)

# Connect to blob service
block_blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)

# Create a list of blobs within the containers
blob_list = block_blob_service.list_blobs(container_name)
for item in blob_list:
    blob_name = item.name
    if blob_name == blob_item:
        # download_path = './downloads/' + blob_name
        # block_blob_service.get_blob_to_path(container_name, blob_name, download_path)
        # print('Downloaded BLOB to ./downloads/ with name: ' + blob_name)
        time.sleep(2)
        print(psutil.virtual_memory())
        time_start = time.time()
        pi = 0
        for i in range(1, cpu_usage):
            a = bytearray(memory_usage)
            getcontext().prec = 100
            pi = sum(1 / Decimal(16) ** k *
                     (Decimal(4) / (8 * k + 1) -
                      Decimal(2) / (8 * k + 4) -
                      Decimal(1) / (8 * k + 5) -
                      Decimal(1) / (8 * k + 6)) for k in range(500000))
            time.sleep(2)
            print(psutil.virtual_memory())
        print('Pi is calculated to be ' + str(pi) + ' ')
        time_end = time.time()
        time_diff = time_end - time_start
        time.sleep(2)
        print(psutil.virtual_memory())
        print('Time required to calculate was ' + str(time_diff) + ' seconds for BLOB container item ' + str(blob_item))
        time.sleep(2)
        print(psutil.virtual_memory())
