import os
import time
import pytz
from datetime import datetime
from kubernetes import client, config

if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
    tz = os.environ['TIME_ZONE']
    timezone = pytz.timezone(tz)
    max_time_diff = int(os.environ['TIME_DIFF_BEFORE_DELETION'])
else:
    config.load_kube_config()
    timezone = pytz.utc
    max_time_diff = 1800

core = client.CoreV1Api()

while True:
    pod_list = core.list_namespaced_pod(namespace='default')
    if len(pod_list.items) != 0:
        for item in pod_list.items:
            item_phase = item.status.phase
            item_datetime_start = item.status.start_time
            now_datetime = datetime.now(timezone)
            diff_datetime = int((now_datetime - item_datetime_start).seconds)
            if item_phase == 'Succeeded' and diff_datetime > max_time_diff:
                delete_options = client.V1DeleteOptions()
                core.delete_namespaced_pod(name=item.metadata.name, namespace='default', body=delete_options)
                pod_name = str(item.metadata.name)
                print('Removed terminated pod ' + pod_name)
    else:
        print('No pods to be deleted.')
    time.sleep(60)
