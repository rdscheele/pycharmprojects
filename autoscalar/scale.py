import os
from azure.servicebus import ServiceBusService, Message, Queue
from kubernetes import client, config

# TODO: Better implementation for declaration of variables
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


# Just for testing
# Connect to existing kubernetes cluster
aToken = 'hUaR7W5ZpTRaTDFcxfiLqOEZTe/c2/hLzmYzdvOUPPg='
aConfiguration = client.Configuration()
aConfiguration.host = 'https://wellcluster-b018dc4b.hcp.westeurope.azmk8s.io'
aConfiguration.verify_ssl = False
aConfiguration.api_key = {"authorization": "Bearer " + aToken}
aApiClient = client.ApiClient(aConfiguration)
print(client.AutoscalingV1Api(aApiClient).list_namespaced_horizontal_pod_autoscaler('default'))
