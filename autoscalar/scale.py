import os
from azure.servicebus import ServiceBusService, Message, Queue
from kubernetes import client, config
import datetime
import time

# TODO: Better implementation for declaration of variables (Maybe config file?)
# Connect to the service bus
bus_service = ServiceBusService(
    service_namespace='wellprototype',
    shared_access_key_name='master',
    shared_access_key_value='2uWqgYUl+0PZerFo4qrVPLj1pOiaZGUHDDnXc8I8Umg=')
# The deployment name to be scaled.
deployment_to_scale_name = 'scaling-processor'
# Time between checking on scaling up and scaling down. Set to 0 if no waiter has to be implemented.
waiter = 5
min_replicas = 0
max_replicas = 10
target_cpu_utilization_percentage = 70
scale_up_messages = 20
scale_down_messages = 10
scale_up_cool_period = 5.0
scale_down_cool_period = 5.0
last_scale_up_time = datetime.datetime.now()
last_scale_down_time = datetime.datetime.now()


# Get the number of queue items from the service bus. Returns integer.
def get_number_of_service_bus_queue_items():
    num_message = int(bus_service.get_queue('wellqueue').message_count)
    return num_message


# Set up an auto scalar. Set target_cpu_utilization_percentage to 0 if not applicable. Returns auto scalar.
'''def make_auto_scalar(min_replicas_spec, max_replicas_spec, target_cpu_utilization_percentage_spec):
    # Load the current configuration
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()

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
    return auto_scalar'''


# Get the deployment for the running auto scalar
def get_running_auto_scalar():
    auto_scalar_deployment = client.AutoscalingV1Api().list_namespaced_horizontal_pod_autoscaler('default')
    print(auto_scalar_deployment)


def scale_up():
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    deployment = client.AppsV1Api().read_namespaced_deployment(name='scaling-processor', namespace='default')
    current_replicas = deployment.spec.replicas

    if not current_replicas <= max_replicas:
        deployment.spec.replicas = current_replicas + 1
        client.AppsV1Api().patch_namespaced_deployment(name='scaling-processor', namespace='default', body=deployment)
    else:
        print('Max pods reached.')


def scale_down():
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    deployment = client.AppsV1Api().read_namespaced_deployment(name='scaling-processor', namespace='default')
    current_replicas = deployment.spec.replicas

    if not current_replicas >= min_replicas:
        deployment.spec.replicas = current_replicas - 1
        client.AppsV1Api().patch_namespaced_deployment(name='scaling-processor', namespace='default', body=deployment)
    else:
        print('Min pods reached.')

# auto_scalar = make_auto_scalar(min_replicas, max_replicas, target_cpu_utilization_percentage)
# pods = client.CoreV1Api().list_pod_for_all_namespaces()

scale_up()

while True:
    number_of_messages = get_number_of_service_bus_queue_items()

    if number_of_messages > scale_up_messages:
        curr_time = datetime.datetime.now()
        elapsed_time = curr_time - last_scale_up_time
        elapsed_time_seconds = elapsed_time.total_seconds()
        if elapsed_time_seconds > scale_up_cool_period:
            print('Scaling up!')
            scale_up()
            last_scale_up_time = datetime.datetime.now()
        else:
            print('Still cooling down, skipping scale up.')

    if number_of_messages < scale_down_messages:
        curr_time = datetime.datetime.now()
        elapsed_time = curr_time - last_scale_down_time
        if elapsed_time.total_seconds() > scale_down_cool_period:
            print('Scaling down!')
            scale_down()
            last_scale_down_time = datetime.datetime.now()
        else:
            print('Still cooling down, skipping scale down.')

    if waiter != 0:
        time.sleep(waiter)
