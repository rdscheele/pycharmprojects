import os
import time
import pytz
from datetime import datetime
from kubernetes import client, config

# Get environment variables. These should be defined in the YAML when creating the deployment.
if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
    # Timezone is based on where the cluster is hosted, will be UTC for clusters hosted in EUW
    tz = os.environ['TIME_ZONE']
    timezone = pytz.timezone(tz)
    # How long ago a pod has to be created before being deleted in seconds
    max_time_diff = int(os.environ['TIME_EXPIRED_BEFORE_DELETION'])
    # Set the namespace where the pods are located
    namespace = os.environ['POD_NAMESPACE']
    # How long the cleanup waits before checking for pods and executing again
    sleep_time = os.environ['SLEEP_TIME']
else:
    config.load_kube_config()
    timezone = pytz.utc
    max_time_diff = 1800
    namespace = "default"
    sleep_time = 60

# Load core kubernetes API
core = client.CoreV1Api()

while True:
    # Get the current list of pods in the default namespace
    pod_list = core.list_namespaced_pod(namespace='default').items
    if len(pod_list) != 0:
        for item in pod_list:
            # Get the phase of the pod
            item_phase = item.status.phase
            # Get the start time of the pod
            item_datetime_start = item.status.start_time
            now_datetime = datetime.now(timezone)
            diff_datetime = int((now_datetime - item_datetime_start).seconds)
            # If a pod has status succeeded and has lived longer than specified time
            # A pod gets status.phase succeeded when it has terminated successfully
            # More on phase https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
            if item_phase == 'Succeeded' and diff_datetime > max_time_diff:
                delete_options = client.V1DeleteOptions()
                core.delete_namespaced_pod(name=item.metadata.name, namespace=namespace, body=delete_options)
                pod_name = str(item.metadata.name)
                print('Removed terminated pod ' + pod_name)
    else:
        print('No pods to be deleted.')
    time.sleep(sleep_time)
