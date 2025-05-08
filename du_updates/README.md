# DU Updates

For DU updates, our initial implementation (as demonstrated in the SwapRAN paper) was based on a commercial/proprietary DU using Intel's FlexRAN, which is subjected to NDA restrictions.
As such, we provide an alternative implementation using the open source OpenAirInterface5G stack.

Here, we provide an example usage by adapting OAI's [reference Helm chart](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed).

## Overview

We focus on D-RAN settings, where compute resource are scarce, and spinning up an additional new DU instance concurrent to quickly switch over is not feasible and can cause realtime processes to miss their deadlines, and therefore increasing the downtimes.

In such a case, we have to first kill the old DU, then only start the new DU, which is equivalent to K8S' Recreate strategy. We compare this with SwapRAN.

The key in SwapRAN lies in (1) using OS thread priorities to safely initializing the new DU while overlapping with the new DU, and (2) using the NIC to redirect fronthaul traffic to the new DU. 
We use an LD_PRELOAD library to intercept certain Linux pthread syscalls, and also the K8S's preStop lifecycle hook.

For more details, please refer to the SwapRAN paper.

## Bootstrapping

> IMPORTANT NOTE: Different from the CU updates setup, to test DU updates, we must use a bare metal K8S setup. 
In this example, we have validated it with K3s. Additionally, we assume an O-RAN 7.2x setup.
In our setup, we use an Intel E810XXVDA4TGG1 NIC.

#### Setting up HugePages/ SR-IOV

First, you need to setup HugePages on your system.
This can be done either by using the utility scripts from DPDK, or it can be configured in `grub`.

Next, for the corresponding network interface connected to the DU, you will need to create two VFs with the same MAC addresses.
Then, bind these VFs with `vfio-pci` and make sure to expose them to K8S.

On how to expose SR-IOV VFs to K8S, please consult the following two repositores.
1. [sriov-cni](https://github.com/k8snetworkplumbingwg/sriov-cni)
1. [sriov-network-device-plugin](https://github.com/k8snetworkplumbingwg/sriov-network-device-plugin)

For the configMap fil for the `sriov-network-device-plugin`, you should update the list of resources accordingly (in particular, `intel.com/intel_sriov_dpdk`) to include your two VFs.
In our setup, the VFs are `0000:70:01.0` and  `0000:70:01.1`.
For the other resources, if not used, they can be safely deleted from the configMap file.

Once you have set them up, you can validate them with the following command:

```bash
~$ kubectl get node $HOSTNAME -o json | jq '.status.allocatable'
{
  "cpu": "32",
  "ephemeral-storage": "1793577558043",
  "hugepages-1Gi": "50Gi",
  "hugepages-2Mi": "0",
  "intel.com/intel_sriov_dpdk": "2",
  "memory": "79160000Ki",
  "pods": "110"
}
```

IMPORTANT! There should be allocatable resources detected by K8s under `intel.com/intel_sriov_dpdk` and `hugepages-1Gi`.

#### RAN configurations

Based on your setup, you will need to update the RAN configuration, which includes, but not limited to the `fhi72` section for the DU and RU's, AMF address, other radio frequency related parameters.

#### libswapRAN.so

Compile the LD_PRELOAD library under `src/libswapRAN`.
Then, move `libswapRAN.so` to the `/tmp` folder.

> Note: As the `oai-gnb-fhi72` containers use Ubuntu22m, thus, for compilation, Ubuntu22 or older is required due to the `glibc` being not backwards compatible.

## Experimentation

The following commands used can be found in the `Makefile`. 

Before proceeding, we assume that you have a 5G core up and running already.
For this setup, we recommend using Open5GS. 
You may need to adjust the AMF addresses accordingly.

### Setup 1: Baseline

Bring up both the CU and DU.
```
make baseline-setup-w14
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make baseline-update-w18
```

Observe how the update process affects the UE's traffic. 
Based on our evaluations, the downtime should be at least 25 seconds.

Once you are down, cleanup the RAN.
```
make cleanup
```

### Setup 2: SwapRAN

Bring up both the CU and DU.
```
make swapran-setup-w14
```

Then, connect your UE, and run either ping or iPerf3.
To get accurate results, we advise using smaller reporting intervals. 
An example command for 200ms ping would be: `ping 8.8.8.8 -O -D -i 0.2`.

Next, while the UE is generating traffic, execute an update.
```
make swapran-update-w18
```

Observe how the update process affects the UE's traffic. 
Based on the SwapRAN paper's evaluation with the commercial DU, the downtime using SwapRAN is expected to be around 1-2 seconds.
In our OAI 7.2x setup, we have been observing downtimes to be around 3-5 seconds, which can be attributed to the known less optimal RF performance (which can be improved with further tuning).

## Demo Video Links

Coming soon.

## Limitations

The current implementation with OAI contains some slight differences with the one demonstrated in the SwapRAN paper.
This is due to the inherent differences between the Intel FlexRAN-based commercial DU and OAI DU, especially on how they create/manage the realtime threads.
This explains the why we intercept additional syscalls in `libswapRAN` as compared to only one in the paper.

Other limitations include: 
- The current reference implementation does not support lookaside hardware accelerators (e.g., for LDPC), e.g., Intel ACC200, Intel VRB, Xilinx T2 etc, as running the DPDK BBDEV accelerators in FHI7.2 mode is not supported yet.
Once the implementation is available, we may provide an update in due course.
- DPDK patch to reduce SMI is currently not applied yet.