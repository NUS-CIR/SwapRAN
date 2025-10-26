# CU Updates

For CU updates, our implementation have been validated using OAI's CU.

Here, we provide an example usage by adapting OAI's [reference Helm chart](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed).

## Overview

We compare CU updates using SwapRAN against K8S' vanilla update mechanism.

As a summary, the key in SwapRAN lies in the use of an F1AP proxy and F1AP Reset messages.
At the same time, we use K8S's lifecycle hooks (1) postStart and (2) preStop, to manage the old/new CUs during the update process. 

More details can be found in the SwapRAN paper.

## Bootstrapping

In this example, we have validated SwapRAN with K3s. 
Additionally, we assume an O-RAN 7.2 setup.
In our setup, we use an Intel E810-XXVDA4TGG1 4x25GbE NIC, and we use a LLS-C1 setup between the DU and RU.

### Getting the Container Images

First, you need to get the OAI DU and CU container images.
Also, you need to get the F1AP proxy container image.
To get the images, you can simply run the script `./scripts/prepull_images.sh`.

You can refer to the README under [`./src/f1ap-proxy`](./src/f1ap-proxy/README.md) for more details about the F1AP proxy.

### System Setup

Please refer to the Bootstrapping section in the [README](../du_updates/README.md) for  DU updates section for the necessary system setup steps, including setting up the VFs for the NIC, hugepages, and SR-IOV. 

> Note: If you do not have an O-RAN 7.2 setup but still wish to try out CU updates, you can refer to another implementation for CU updates under the branch `oai-summer-workshop` which runs a Split-8 setup with a DU using the USRP B210.
In that setup, we use Minikube instead of K3s.

## Experimentation

The following commands used can be found in the `Makefile`. 

Before proceeding, we assume that you have a 5G core up and running already.
For this setup, we recommend using Open5GS. 

Once everything is up and running, you can proceed to test CU updates using the baseline setup, or using SwapRAN.

### Setup 1: Baseline

Bring up both the CU and DU.
```
make baseline-setup-w29
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make baseline-update-w30
```

Observe how the update process affects the UE's traffic. 
Based on our evaluations, the downtime should be around 7 seconds.

Once you are at `w30`, you can also try updating to later versions, e.g., `w31` and observe similar downtimes.

Finally, once you are down, cleanup the RAN.
```
make cleanup
```

### Setup 2: SwapRAN

Bring up both the CU and DU.
```
make swapran-setup-w29
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make swapran-update-w30
```

Observe how the update process affects the UE's traffic. 
Based on our evaluations, the downtime using SwapRAN should be around 1-2 seconds.

Once you are at `w30`, you can also try updating to later versions, e.g., `w31` and observe similar downtimes.

Finally, once you are down, cleanup the RAN.
```
make cleanup
```

## Demo Video Links

A recorded demo of SwapRAN using OAI can be found here:
- Coming soon.

An earlier demo of SwapRAN at the OAI Summer Workshop 2025 can be found here:
- [OAI Summer Workshop 2025](https://youtu.be/7xD2kYkpmOM) 

## Additional Notes

### Using different gNB IDs

In SwapRAN, as we run two CU instances concurrently during the update process, we will need to make sure that both CU instances do not share the same gNB ID, as this will cause the core network to reject the NG setup request from the new CU.

Therefore, in practice, we will need to reserve an additional "sister" gNB ID for SwapRAN to work.
In our setup, we alternate between two gNB IDs, i.e., `0xe0` and `0xe1`.

### Limitations

- In this reference implementation, the Python-based F1AP proxy only demonstrates the process of updating the CU for one DU.
To support multiple DUs, the current F1AP proxy needs to be extended to manage multiple F1AP connections accordingly.

- The current Python F1AP proxy is meant to be a prototype implementation for demonstrating SwapRAN.
For production-level use cases, it is recommended to implement the F1AP proxy in a compiled language such as C/C++ for better performance and better support for ASN.1 PER encoding/decoding.

- gNB-DU-ConfigurationUpdate/gNB-CU-ConfigurationUpdate procedure is not supported in the current F1AP proxy implementation as OAI does not currently support it at the time of writing. Technically, the F1AP proxy only needs to cache these messages, and replay them at the same order accordingly. 

