# DU Updates

For DU updates, our initial implementation (as demonstrated in the SwapRAN paper) was based on a commercial/proprietary DU using Intel's FlexRAN, which is subjected to NDA restrictions.
As such, we provide an alternative implementation using the open source OpenAirInterface5G stack.

Here, we provide an example usage by adapting OAI's [reference Helm chart](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed).

## Overview

We focus on D-RAN settings, where compute resource are scarce, and spinning up an additional new DU instance concurrent to quickly switch over is not feasible and can cause realtime processes to miss their deadlines, and therefore increasing the downtimes.
In such a case, we have to first kill the old DU, then only start the new DU, which is equivalent to K8S' Recreate strategy. 
We compare this with SwapRAN.

In SwapRAN, we start by launching the new DU instance while the old DU is still running.
The key in SwapRAN lies in (1) using OS thread priorities to initalize the new DU while overlapping with the old DU -- we interleave the realtime (RT) parts of the DU process safely so that they do not interfere with each other, and (2) using the NIC to redirect fronthaul traffic to the new DU.
We use an LD_PRELOAD library (`libswapRAN.so`) to intercept certain Linux pthread syscalls made by the DU, and also K8S's preStop lifecycle hook.

For more details, please refer to the SwapRAN paper.

## Bootstrapping

In this example, we have validated SwapRAN with K3s. 
Additionally, we assume an O-RAN 7.2 setup.
In our setup, we use an Intel E810-XXVDA4TGG1 4x25GbE NIC, and we use a LLS-C1 setup between the DU and RU.

### Getting the Container Images

First, you need to get the OAI DU and CU container images.
For SwapRAN, as we introduced optimizations to allow the DU to start faster, we need use an optimized DU image.
To get the images, you can simply run the script `./scripts/prepull_images.sh`.

If you are interested to know what are the patches applied to the DU, please refer to the README under [`./src/xRAN-patch`](./src/xRAN-patch/README.md).

### Setting up the VFs

You need to create two Virtual Functions (VFs) for the Intel E810-XXVDA4TGG1 4x25GbE NIC. 
Using `ens6f0np0` as an example interface name, you can use the following commands to create two VFs, and bind them with `vfio-pci`.
One VF will be used by the old DU, while the other VF will be used by the new DU during the update process in an alternate manner.

```bash
sudo ethtool -G ens6f0np0 rx 8160
sudo ethtool -G ens6f0np0 tx 8160

# create 2 VFs
sudo modprobe iavf
sudo sh -c 'echo 0 > /sys/class/net/ens6f0np0/device/sriov_numvfs'
sudo sh -c 'echo 2 > /sys/class/net/ens6f0np0/device/sriov_numvfs'

# configure the VFs (e.g., MAC address, VLAN, MTU etc)
sudo ip link set ens6f0np0 vf 0 mac aa:bb:cc:dd:ee:ff vlan 5 qos 0 spoofchk off trust on mtu 9600
sudo ip link set ens6f0np0 vf 1 mac aa:bb:cc:dd:ee:ff vlan 5 qos 0 spoofchk off trust on mtu 9600

# bind the VFs to vfio-pci
sudo /usr/local/bin/dpdk-devbind.py --unbind 70:01.0
sudo modprobe vfio-pci
sudo /usr/local/bin/dpdk-devbind.py --bind vfio-pci 70:01.0
sudo /usr/local/bin/dpdk-devbind.py --unbind 70:01.1
sudo modprobe vfio-pci
sudo /usr/local/bin/dpdk-devbind.py --bind vfio-pci 70:01.1
```

Note that the MAC addresses assigned to the two VFs are the same -- this allows SwapRAN to seamlessly switch between the two DUs without needing to reconfigure the RU.
When the same MAC address is used, the eSwitch on the NIC will automatically mirror the incoming packets to both VFs.

### Setting up HugePages/ SR-IOV

Next, you need to setup HugePages on your system.
This can be done either by using the utility scripts from DPDK, or it can be configured in `grub`.

For the corresponding network interface connected to the DU, you should already created two VFs with the same MAC addresses and bind these VFs with `vfio-pci` as per the earlier section.  

Now, we need to make sure that K8S can see these HugePages and SR-IOV VFs.
On how to expose SR-IOV VFs to K8S, please consult the following two repositories.
1. [sriov-cni](https://github.com/k8snetworkplumbingwg/sriov-cni)
1. [sriov-network-device-plugin](https://github.com/k8snetworkplumbingwg/sriov-network-device-plugin)

For the configMap file for the `sriov-network-device-plugin`, you should update the list of resources accordingly (in particular, `intel.com/intel_sriov_dpdk`) to include your two VFs.
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

**IMPORTANT!** There should be allocatable resources detected by K8s under `intel.com/intel_sriov_dpdk` and `hugepages-1Gi`.

### RAN configurations

Based on your setup, you will need to update the RAN configuration, which includes, but not limited to the `fhi72` section for the DU and RU's, AMF address, other radio frequency related parameters.
The RAN configuration are located under `templates/configmap.yaml`.

### libswapRAN.so

Compile the LD_PRELOAD library under `src/libswapRAN`.
Then, copy `libswapRAN.so` to the `/tmp` folder.

> Note: As the `oai-gnb-fhi72` containers use Ubuntu 22.04, thus, for compilation, Ubuntu22 or older is required due to the `glibc` being not backwards compatible. Therefore, we have provided a handy script (`build_libswapRAN.sh`) which compiles the library inside an Ubuntu 20.04 container.

## Experimentation

The following commands used can be found in the `Makefile`. 

Before proceeding, we assume that you have a 5G core up and running already.
For this setup, we recommend using Open5GS. 

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
Based on our evaluations, the downtime should be at least 25 seconds.

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
Based on the SwapRAN paper's evaluation with the commercial DU, the downtime using SwapRAN is expected to be around 1-2 seconds.
In our setup, we have been observing downtimes to be around 3-5 seconds, which can be attributed to the known less optimal RF performance with our configuration which can be improved with further tuning.

Once you are at `w30`, you can also try updating to later versions, e.g., `w31` and observe similar downtimes.

Finally, once you are down, cleanup the RAN.
```
make cleanup
```

## Demo Video Links

A recorded demo of SwapRAN using OAI can be found here:
- [MobiCom25](https://youtu.be/1CDkb3xzo4c).

An earlier demo of SwapRAN at the OAI Summer Workshop 2025 can be found here:
- [OAI Summer Workshop 2025](https://youtu.be/EKVyJjPpaG8).

## Additional Notes

### Using different DU and PCI IDs
In SwapRAN, as we run two DU instances concurrently during the update process, we will need to make sure that both DU instances do not share the same DU ID and physical cell ID (PCI), as this will cause the CU to reject the F1 setup request from the new DU.

Therefore, in practice, we will need to reserve an additional "sister" DU ID and PCI for SwapRAN to work.
In our setup, we alternate between two sets of `duId`, `nr_cellid`, `phyCellId`, i.e., (0xe000, 11111111L, 0) and (0xe001, 22222222L, 1).

### Limitations
The current implementation with OAI contains some slight differences with the one demonstrated in the SwapRAN paper.
This is due to the inherent differences between the Intel FlexRAN-based commercial DU and OAI DU, especially on their initialization process and how they create/manage the realtime threads.
This explains the additional delay experienced in the new DU starting (contributing to the overall downtime), and why we intercept additional syscalls in `libswapRAN` as compared to only one in the paper.

Other limitations include: 
- DPDK patch to reduce SMI is currently not applied.
- The current reference implementation does not support lookaside hardware accelerators (e.g., for LDPC), e.g., Intel ACC200, Intel VRB, Xilinx T2 etc, as running the DPDK BBDEV accelerators in FHI7.2 with OAI was not supported as of `2025.w31` (when this demo was prepared). Extending SwapRAN to support lookaside accelerators should be straightforward by simply exposing the accelerator's VF to K8S when setting up SR-IOV.