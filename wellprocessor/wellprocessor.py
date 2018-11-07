import os
from azure.servicebus import ServiceBusService, Message, Queue
from azure.storage.blob import BlockBlobService

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
    block_blob_service = BlockBlobService(account_name='bbwelldata', account_key='fK2i08pNdKOB6nHQYwvvS42EJBegLRlHvqz3IBKsxMkVhkfjmNQJMLzZjFJ71Mnf5+G67t4ajR6usvHLNJVilA==')

    # Create a list of blobs within the containers
    blob_list = block_blob_service.list_blobs(container_name)
    for item in blob_list:
        blob_name = item.name
        if blob_name == blob_item:
            download_path = './downloads/' + blob_name
            block_blob_service.get_blob_to_path(container_name, blob_name, download_path)
            print('Downloaded BLOB to ./downloads/ with name: ' + blob_name)
else:
    print('No items in queue')