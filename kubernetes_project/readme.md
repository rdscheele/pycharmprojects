**Readme**

This example consists of multiple Python files. It also requires something that sends messages to a service bus queue.
I have created a small frontend application that sends messages to the service bus queue in C# with just one click on a
button. It can be found here.

https://github.com/rdscheele/repos

This project contains
- podcleanup.py. This is used to clean up pods with status 'Terminated: Succeeded'
- podqueue.py. This is the manager, it will create pods with container for each message.
- wellprocessor.py. This is the container pod that is created by the manager.
- testfile.py. Contains a few unit tests.


**Requirements**

- (*Optional*)
To Dockerize the code yourself you require Docker to be installed on your machine. Otherwise use the *rdscheele/* Docker
repositories.
- Azure subscription
- Azure Service Bus namespace with two queues: *activequeue* and *wellqueue*
- Azure Storage Account
- Azure Kubernetes Cluster with at least one node.
- Azure CLI on your local machine. (If you can live with using *az aks browse ...*)
- (*Optional*) Kubectl on your local machine. (If you want to use kubectl instead)

**How to run**

(*Optional*) Dockerize the *wellprocessor.py* and *podqueue.py*

Run `az login` with your credentials.

Run `az aks get-credentials --resource-group <YOUR RESOURCE GROUP> --name <NAME OF CLUSTER>`

Send a message to the service bus queue with the following format where everything between the brackers is a string.
This can be done with the Visual Studio project mentioned above (Make sure to fill in the keys in the project).

`sub-domain;messageId;numberOfMessagesInBatch;fakeCpuValueToBeUsed;fakeMemoryValueToBeUsed`

Fill in the variables in `queue_manager/podqueue.py` at the top.

Run `queue_manager/podqueue.py`. It should now create pods on your cluster.

The podqueue.py can be ran inside the cluster as well, making this process fully automatic.