FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y netcat iproute2 libsctp-dev libsctp1 lksctp-tools python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install pysctp pycrate Flask

WORKDIR /root
COPY ./f1ap_proxy.py .
COPY ./f1ap.py .