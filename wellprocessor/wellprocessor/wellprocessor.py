import os
from azure.storage.blob import BlockBlobService
import time
from decimal import Decimal, getcontext
import random

container_name = os.environ['CONTAINER_NAME']
blob_item = os.environ['BLOB_ITEM']
storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']

# Connect to blob service
block_blob_service = BlockBlobService(account_name=storage_account_name, account_key=storage_account_key)

# Create a list of blobs within the containers
blob_list = block_blob_service.list_blobs(container_name)
for item in blob_list:
    blob_name = item.name
    if blob_name == blob_item:
        download_path = './downloads/' + blob_name
        # block_blob_service.get_blob_to_path(container_name, blob_name, download_path)
        # print('Downloaded BLOB to ./downloads/ with name: ' + blob_name)

        time_start = time.time()
        random_number = random.randint(1, 20)
        for i in range(1, random_number):
            a = bytearray(812000000)
            getcontext().prec = 100
            random_number = random.randint(100000, 800000)
            pi = sum(1 / Decimal(16) ** k *
                     (Decimal(4) / (8 * k + 1) -
                      Decimal(2) / (8 * k + 4) -
                      Decimal(1) / (8 * k + 5) -
                      Decimal(1) / (8 * k + 6)) for k in range(random_number))
        time_end = time.time()
        time_diff = time_end - time_start
        print('Time required to calculate was ' + str(time_diff) + ' seconds for container ' + str(container_name))
