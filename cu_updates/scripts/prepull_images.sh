#! /bin/bash

set -x

minikube ssh -- docker pull khooi8913/f1ap_proxy:swapran
minikube ssh -- docker pull oaisoftwarealliance/oai-gnb:2024.w40
minikube ssh -- docker pull oaisoftwarealliance/oai-gnb:2024.w41
minikube ssh -- docker pull oaisoftwarealliance/oai-gnb:2024.w42
minikube ssh -- docker pull oaisoftwarealliance/oai-gnb:2024.w43