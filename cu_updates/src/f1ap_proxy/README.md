# F1AP Proxy

The F1AP proxy is used to preserve the stateful connection between the CU and the DU, especially during CU updates.
In deployments, the DU connects to the F1AP proxy, which in turn connects to the CU.

During CU updates, from the DU's perspective, the CU remains available, while the old CU is replaced with the new CU.
In this process, the F1AP proxy will perform the F1 Setup process with the new CU, and at the same time, trigger an F1 Reset to the DU to reinitialize the UE states at the DU.

## Usage

At the DU config, change the CU's IP to point to the F1AP proxy.
An example to start the proxy would be:

```bash
python3 f1ap_proxy.py --proxy-ip F1AP_PROXY_CONTAINER_IP
```