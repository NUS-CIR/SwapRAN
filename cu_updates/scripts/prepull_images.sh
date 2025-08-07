#! /bin/bash

set -x

sudo ctr image pull docker.io/khooi8913/f1ap_proxy:swapran
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb:2025.w29
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb:2025.w30
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb:2025.w31
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb-fhi72:2025.w29
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb-fhi72:2025.w30
sudo ctr image pull docker.io/oaisoftwarealliance/oai-gnb-fhi72:2025.w31
sudo ctr image pull docker.io/oaisoftwarealliance/oai-tcpdump-init:alpine-3.20