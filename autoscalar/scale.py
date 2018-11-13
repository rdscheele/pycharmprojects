import os
from azure.servicebus import ServiceBusService, Message, Queue
from kubernetes import client, config

# TODO: Better implementation for declaration of variables (Maybe config file?)
bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')
min_replicas = 0
max_replicas = 10
target_cpu_utilization_percentage = 70


# Get the number of queue items from the service bus
def get_number_of_service_bus_queue_items():
    number_of_messages = bus_service.get_queue('wellqueue').message_count
    return number_of_messages


# Set up an auto scalar. Set target_cpu_utilization_percentage to 0 if not applicable.
def make_auto_scalar(min_replicas_spec, max_replicas_spec, target_cpu_utilization_percentage_spec):
    auto_scalar = client.V1HorizontalPodAutoscaler()
    auto_scalar.metadata = client.V1ObjectMeta()
    auto_scalar.metadata.name = 'processor_auto_scalar'
    auto_scalar.spec = client.V1HorizontalPodAutoscalerSpec
    auto_scalar.spec.min_replicas = min_replicas_spec
    auto_scalar.spec.max_replicas = max_replicas_spec
    if 0 < target_cpu_utilization_percentage_spec < 100:
        auto_scalar.spec.target_cpu_utilization_percentage = target_cpu_utilization_percentage_spec
    elif target_cpu_utilization_percentage_spec == 0:
        print('No target_cpu_utilization_percentage parameter set.')
    else:
        print('Illegal target_cpu_utilization_percentage_spec given.')
    return auto_scalar


# Deploy the auto scalar
def deploy_auto_scalar():
    # Load the current configuration
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    # Create the auto scalar deployment
    auto_scalar_api = client.AutoscalingV1Api()
    auto_scalar = make_auto_scalar(min_replicas, max_replicas, target_cpu_utilization_percentage)
    auto_scalar_api.create_namespaced_horizontal_pod_autoscaler('default', auto_scalar)


# Get the deployment for the running auto scalar
def get_running_auto_scalar():
    auto_scalar_deployment = client.AutoscalingV1Api().list_namespaced_horizontal_pod_autoscaler('default')
    print(auto_scalar_deployment)


def scale_up():
    return 0


def scale_down():
    return 0

deploy_auto_scalar()
# Just for testing
# Connect to existing kubernetes cluster
'''aToken = 'ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklpSjkuZXlKcGMzTWlPaUpyZFdKbGNtNWxkR1Z6TDNObGNuWnBZMlZoWTJOdmRXNTBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5dVlXMWxjM0JoWTJVaU9pSmtaV1poZFd4MElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WldOeVpYUXVibUZ0WlNJNkltUmxabUYxYkhRdGRHOXJaVzR0TjIxd2VISWlMQ0pyZFdKbGNtNWxkR1Z6TG1sdkwzTmxjblpwWTJWaFkyTnZkVzUwTDNObGNuWnBZMlV0WVdOamIzVnVkQzV1WVcxbElqb2laR1ZtWVhWc2RDSXNJbXQxWW1WeWJtVjBaWE11YVc4dmMyVnlkbWxqWldGalkyOTFiblF2YzJWeWRtbGpaUzFoWTJOdmRXNTBMblZwWkNJNkltUTNNamhqTW1ReExXVTJOek10TVRGbE9DMWhZMk5sTFRBMllUSTROREkxTXpVMFl5SXNJbk4xWWlJNkluTjVjM1JsYlRwelpYSjJhV05sWVdOamIzVnVkRHBrWldaaGRXeDBPbVJsWm1GMWJIUWlmUS5PX1VKMUVfemFjMS1NcTliSzhGWUk4QlVIOU5SYmVXUnI1UzdCamNkSWFveDR3X0ZKYVhzbjdOM2NHWkwyakxqQ0kxSUtUM19HQmxtY0dQN1VZeUpCbEJEb0J0TVNVTUNpa2l2UnZoOFBKTzZLZWVHSnFYbTcwWUdXU25feXhqZWpwSGd1SWZLakpub0JzTXVPTW5BX2FIclhiS3BBYWQ1WkpXOFFZTkhCbzIyWVhJZERfWTJFUUMzRTZPbjhXRHg3ckV1djdYN1VQYVJIS0JxVVdXMzdLNjJQa1lhNkltY09TVjhiVlN0VWo3Z2NGdWZoaE9La3VHNDRGdXNqRDN6aEp1YTdfZFlmaFpCd1dBNHdubTRTYWozTGdtcnVGbGNfbDcyRzVUS3lPZDVSbXZVY09pVWl6N0pkOF9HLUhNWUxzVkZBb0dpbW1xZWt3UUhUSV96SEJxcnVrWm5Pb3h5T3pRZjJad3pkaV9pU1M1MGx4TDVkU1hQVUFkaUJRRUJyT3RkWk5McERteWxCWnRRNVVLVXJtLWVBS1Y4VlhucERuQ2dubUMzdjF4V1Y1MDZ2ckRmS2RmSHJpSU9ETThwOVBLZDhUWmlNTEUydmpDd3A5WGhRX045U01iSDdMVDd3RjI5bHFGZnpKSEo0cGV3NFVFT3g2aW9JYV9xOThVdkJERm0xR0phR3pHY1poOXkzTUw2aEZXRHd0aEhQd25yQnNhSzN6TGJ4aWk4TjFyQWZFZjlTcmUwRGtTdkhfcHFwNVI0SlRCeFFfd1Z4dzZBWTBMWUQzb1dNWE1QS0FfWkNrZHp4ZkotdEQxRFBCekloOXliZldLQ1I4cFNXLUZMajFSMmttZVp6R2ROekkybk5KS1VaV0ZvdXhfNlpxanlsNFVaaW4xZDFaUQ== '
aConfiguration = client.Configuration()
aConfiguration.host = 'https://wellcluster-b018dc4b.hcp.westeurope.azmk8s.io:443'
aConfiguration.verify_ssl = False
#aConfiguration.api_key_prefix['authorization'] = 'Bearer'
aConfiguration.api_key = {"authorization": "Bearer " + aToken}
aApiClient = client.ApiClient(aConfiguration)
v1 = client.CoreV1Api(aApiClient)
print(v1.list_pod_for_all_namespaces(watch=False))'''
#config.load_kube_config()
#v1 = client.CoreV1Api()
#print(v1.list_pod_for_all_namespaces(watch=False))
