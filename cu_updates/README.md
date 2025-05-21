# CU Updates

For CU updates, our implementation have been validated using OAI's CU.

Here, we provide an example usage by adapting OAI's [reference Helm chart](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed).

## Overview

We compare CU updates using SwapRAN against K8S' vanilla update mechanism.

As a summary, the key in SwapRAN lies in the use of an F1AP proxy and F1AP Reset messages.
At the same time, we use K8S's lifecycle hooks (1) postStart and (2) preStop, to manage the old/new CUs during the update process. 

More details can be found in the SwapRAN paper.

## Requirements

> IMPORTANT NOTE: We have only validated this implementation using Minikube, together with a USRP B210. 
Thus, if you are using any other K8s implementation/ radio frontend, you will need to perform adaptations accordingly.

To use Minikube with the USB3-based USRP B210, you will need to mount `/dev` before starting the cluster:
```
minikube start --mount --mount-string="/dev:/dev"
```

The OAI CU/DU setup requires multiple network interfaces to be available. 

The key use cases are (1) to have multiple network interfaces per container, and (2) the ability for us to use static IP addressing for certain network interfaces. To that end, we need the Multus CNI to be available. So, you will need to install it through:
```
kubectl apply -f https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/master/deployments/multus-daemonset.yml
```

Additionally, we use Helm to manage the setup. You can install it using the following:
```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Finally, to ensure smooth experimentation, we recommend you to pre-pull the required images.
For that purpose, you can use the provided script.
Again, if you are not using Minikube, you will need to adapt it accordingly.
```
./scripts/prepull_images.sh
```

## Experimentation

The following commands used can be found in the `Makefile`. 

### Bootstrapping
First, start up a 5G core and iPerf3 instance.
> Note: You may need to update the UE database to add your UE's IMSI etc.
```
make bootstrap
```

Once everything is up and running, you can proceed to test CU updates using the baseline setup, or using SwapRAN.

### Setup 1: Baseline

Bring up both the CU and DU.
```
make baseline-setup-w40
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make baseline-update-w41
```

Observe how the update process affects the UE's traffic. 
Based on our evaluations, the downtime should be around 7 seconds.

Repeat with `w42` and `w43` (technically, you can also perform a downgrade).

Once you are down, cleanup the RAN.
```
make remove_ran
```

### Setup 2: SwapRAN

Bring up both the CU and DU.
```
make swapran-setup-w40
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make swapran-update-w41
```

Observe how the update process affects the UE's traffic. 
Based on our evaluations, the downtime using SwapRAN should be around 1-2 seconds.

Repeat with `w42` and `w43` (technically, you can also perform a downgrade).

## Demo Video Links

- [OAI Summer Workshop 2025](https://youtu.be/7xD2kYkpmOM) 

## Limitations

Known limitations:
- The F1AP proxy currently only supports 1 DU per instance. 
Multi-DU support will come later. 
To support multi-DU setups, the current approach is to use multiple F1AP proxy instances for each DU.