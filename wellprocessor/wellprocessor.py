from azure.servicebus import ServiceBusService, Message, Queue

bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')

a = bus_service.get_queue('wellqueue').message_count

#for i in range(0,a):
msg = bus_service.receive_queue_message('wellqueue', peek_lock=False)
print(msg.body)
#print('Queue empty')

