#! /bin/bash

docker build -t f1ap_proxy .
docker tag f1ap_proxy:latest khooi8913/f1ap_proxy:swapran
docker push khooi8913/f1ap_proxy:swapran