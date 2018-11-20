from azure.servicebus import ServiceBusService, Message, Queue
from azure.storage.blob import BlockBlobService
import time
from decimal import Decimal, getcontext
import random
import ctypes

# Connect to service bus
bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')

# Get the amount of messages in the queue
a = bus_service.get_queue('wellqueue').message_count

if a != 0:
    # Get the top most message
    msg = bus_service.receive_queue_message('wellqueue', peek_lock=False)

    # Reconstruct the message to be a list
    msg_body = str(msg.body)
    msg_body = msg_body[2:]
    msg_body = msg_body[:-1]
    msg_list = msg_body.split(';')
    container_name = msg_list[0]
    blob_item = msg_list[1]

    print('Message list: ' + str(msg_list))

    # Connect to blob service
    block_blob_service = BlockBlobService(account_name='bbwelldata',
                                          account_key='jH9MnJI2M7QMZAgAmmYybD7fUYKIzWg45q6lmZqEO4QuhtP1qy3ocsB8YuBuAdEFwgbJFpE1XIGn/ywmSWlrkg==')

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
            print('Time required to calculate was ' + str(time_diff) + ' seconds')

else:
    print('No items in queue')
    time.sleep(20)
