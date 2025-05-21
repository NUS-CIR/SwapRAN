# SwapRAN - How to Update Your 5G vRAN

This repository holds a reference implementation using the OpenAirInterface5G stack for the live update mechanism presented in the ACM MobiCom'25 paper, "How to Update Your 5G vRAN".

Link to paper: [Google Drive](https://drive.google.com/file/d/1FjyjtAKQYPYTRNaaDy3oc8-ZcpY3PuV0/view?usp=drive_link).

## Overview

SwapRAN proposes techniques that enables the CU/DU update process to be performed seamlessly by reducing the downtimes due to updates, substantially.
For DU updates, the key lies in how to overlap the old DU and the new DU, while sharing the same CPU set and fronthaul NIC.
As for CU updates, we decouple the stateful connection between the CU and DU, and using F1 Resets to gradually migrate DUs to use the new CU during updates.

For DU updates, please refer to the README under `du_updates/`.
> Note: Pay attention the K8S lifecycle hooks, the use of `libswapRAN.so` in the start up command, and also the DU configurations.

As for CU updates, please refer to the README under `cu_updates/`.
> Note: Pay attention to the K8S lifecycle hooks, the use of the F1AP proxy, and also the CU configurations.

## Citation

If you find this work useful, please cite the following:
```
@INPROCEEDINGS{2025-MOBICOM-SwapRAN,
  author={Xin Zhe Khooi and Anuj Kalia and Mun Choon Chan},
  booktitle={ACM MobiCom}, 
  title={{How to Update Your 5G vRAN}}, 
  year={2025}
}
```

## License

The components introduced by SwapRAN, are licensed under the MIT license, which is included in this repository.
The list of components are as follows:
- DU updates
    - K8s preStop hooks
    - libswapRAN.so
    - xRAN-patch 

- CU updates
    - K8s postStart hooks
    - K8s preStop hooks
    - F1AP proxy

Unless otherwise specified, the helm charts included in this repo, which we use/modify to demonstrate SwapRAN, fall under the [OAI Public License V1.1](https://openairinterface.org/legal/oai-public-license/).

## Contact

For any questions, or if you have any comments or feedback, there are two ways to reach out.

- File a GitHub issue under this repo.
- Drop an email to `khooixz [at] comp [dot] nus [dot] edu [dot] sg`.