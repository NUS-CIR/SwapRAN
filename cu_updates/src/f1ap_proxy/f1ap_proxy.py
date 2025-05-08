import sys
import socket
import select
import argparse
import threading
import sctp
import time
import queue
from enum import Enum, auto
from f1ap import *
from pprint import pprint
from typing import List
from threading import Thread
from flask import Flask, jsonify, request, cli

reset_f1ap_pdu_obj = ('initiatingMessage', 
    {
        'procedureCode': 0,
        'criticality': 'reject',
        'value': 
        ('Reset', 
            {
                'protocolIEs': [
                    {'id': 78, 'criticality': 'reject', 'value': ('TransactionID', 1)}, 
                    {'id': 0, 'criticality': 'ignore', 'value': ('Cause', ('misc', 'om-intervention'))}, 
                    {'id': 48, 'criticality': 'reject', 'value': ('ResetType', ('f1-Interface', 'reset-all')
                    )},
                ]
            }
        )
    }
)
class CUConnectionObject():
    def __init__(self, cu_socket, cu_ip, cu_port, version):
        self.cu_socket = cu_socket
        self.cu_ip = cu_ip
        self.cu_port = cu_port
        self.version = version
        self.is_removed = threading.Event()
        self.f1_setup_state = None

class DUConnectionObject():
    def __init__(self, du_socket, du_ip, du_port):
        self.du_socket = du_socket
        self.du_ip = du_ip
        self.du_port = du_port
        self.f1_setup_state = None
        self.f1_setup_req_msg = None

class CUPoolObject():
    def __init__(self):
        self.curr_cu_idx = 0
        self.ptr_idx = 0
        self.cu_pool = [None, None]

    # TODO: enforce CU checking logic here later
    # do not allow duplicate CU connections, and also older CU versions    
    def add_cu(self, cu_obj: CUConnectionObject):
        self.ptr_idx = 1 if self.cu_pool[0] else 0
        self.cu_pool[self.ptr_idx] = cu_obj

    def get_current_cu(self):
        return self.cu_pool[self.curr_cu_idx] if self.cu_pool[self.curr_cu_idx] else None
    
    def get_next_cu(self):
        return self.cu_pool[(self.curr_cu_idx + 1) % 2] if self.cu_pool[(self.curr_cu_idx + 1) % 2] else None

    def retire_current_cu(self):
        assert self.cu_pool[0] and self.cu_pool[1]
        self.cu_pool[self.curr_cu_idx].cu_socket.close() 
        self.cu_pool[self.curr_cu_idx].is_removed.set()
        self.cu_pool[self.curr_cu_idx] = None
        self.curr_cu_idx = (self.curr_cu_idx + 1) % 2

cu_pool = CUPoolObject()
du_obj = None

q = queue.Queue()
is_upgrade_completed = True

app = Flask(__name__)

def get_message_type(data):
    f1ap_pdu = F1AP_PDU_Descriptions.F1AP_PDU
    f1ap_pdu.from_aper(data)
    f1ap_pdu = f1ap_pdu()
    message_type = f1ap_pdu[1]['value'][0] 
    # print(message_type)
    return message_type

def handle_messages():
    global du_obj
    global cu_pool

    print(f"[Message Handler] Starting Message Handler...")
    while True:
        data, from_obj = q.get()
        data_type = get_message_type(data)

        if data_type == "ResetAcknowledge":
            continue

        origin = "DU" if from_obj == du_obj else "CU"
        if origin == "DU":
            print(f"[Message Handler] Received {data_type} from DU {from_obj.du_ip}:{from_obj.du_port}")
            cu_pool.get_current_cu().cu_socket.sctp_send(data, ppid=socket.htonl(62))
            print(f"[Message Handler] Sending to CU {cu_pool.get_current_cu().cu_ip}:{cu_pool.get_current_cu().cu_port}")
        else:
            print(f"[Message Handler] Received {data_type} from CU {from_obj.cu_ip}:{from_obj.cu_port}")
            du_obj.du_socket.sctp_send(data, ppid=socket.htonl(62))
            print(f"[Message Handler] Sending to DU {du_obj.du_ip}:{du_obj.du_port}")

is_du_setup = False
def handle_CU_connection(cu_obj: CUConnectionObject):
    print(f"Started CU Handler for {cu_obj.cu_ip}:{cu_obj.cu_port}")
    
    global du_obj
    global cu_pool
    global is_du_setup

    # NOTE: Do not send F1SetupRequest until the CU becomes the primary.
    # This is to ensure compatibility with CapG which will trigger gNB-CUConfigurationUpdates
    # after F1SetupRequest is sent.
    while cu_pool.get_current_cu() != cu_obj:
        print(f"[CU Handler] Waiting for CU {cu_obj.cu_ip}:{cu_obj.cu_port} to become primary...")
        time.sleep(1)
        pass

    # Wait for the DU to send F1SetupRequest
    while not du_obj or not is_du_setup:
        if du_obj:
            if du_obj.f1_setup_state == "F1SetupRequest":
                if du_obj.f1_setup_req_msg:
                    is_du_setup = True
        else:
            print(f"[CU Handler] Waiting for DU to send F1SetupRequest...")
            time.sleep(1)

    cu_obj.cu_socket.sctp_send(du_obj.f1_setup_req_msg, ppid=socket.htonl(62))
    cu_obj.cu_f1setup_state = "F1SetupRequest"
    
    while True and not cu_obj.is_removed.is_set():
        readable, writeable, exceptional = select.select([cu_obj.cu_socket], [], [], 5)
        if cu_obj.cu_socket in readable and not cu_obj.cu_socket._closed:
            fromaddr, flags, data, _notif = cu_obj.cu_socket.sctp_recv(8192)
            # TODO: Handle SCTP shutdown properly
            data_type = get_message_type(data)
            print(f"[CU Handler] Received {data_type} from CU {cu_obj.cu_ip}:{cu_obj.cu_port}")
            if data_type == "F1SetupResponse":
                if du_obj.f1_setup_state == "F1SetupResponse":
                    cu_obj.cu_f1setup_state = "F1SetupResponse"
                else:
                    du_obj.du_socket.sctp_send(data, ppid=socket.htonl(62))
                    cu_obj.cu_f1setup_state = "F1SetupResponse"
                    du_obj.f1_setup_state = "F1SetupResponse"
                print(f"[CU Handler] F1Setup complete for CU {cu_obj.cu_ip}:{cu_obj.cu_port}")
            else:
                q.put((data, cu_obj))
    print(f"Stopped CU Handler for {cu_obj.cu_ip}:{cu_obj.cu_port}")

def handle_DU_connection(du_obj: DUConnectionObject):
    print(f"Started DU Handler for {du_obj.du_ip}:{du_obj.du_port}")
    while True:
        fromaddr, flags, data, _notif = du_obj.du_socket.sctp_recv(8192)
        # TODO: Handle SCTP shutdown properly
        data_type = get_message_type(data)
        print(f"[DU Handler] Received {data_type} from DU {du_obj.du_ip}:{du_obj.du_port}")
        if data_type == "F1SetupRequest":
            du_obj.f1_setup_req_msg = data
            du_obj.f1_setup_state = "F1SetupRequest"
        else:
            q.put((data, du_obj))

def start_f1ap_proxy(proxy_ip, proxy_port, is_debug):
    global du_obj

    message_handler = threading.Thread(target=handle_messages)
    message_handler.start()

    f1ap_proxy_socket = sctp.sctpsocket_tcp(socket.AF_INET)
    f1ap_proxy_socket.bind((proxy_ip, proxy_port))
    f1ap_proxy_socket.listen(1)

    print(f"[F1AP proxy] DU handler listening on [SCTP] {proxy_ip}:{proxy_port}")
    du_socket, addr = f1ap_proxy_socket.accept()
    du_obj = DUConnectionObject(du_socket, addr[0], addr[1])
    du_handler = threading.Thread(target=handle_DU_connection, args=(du_obj,))
    du_handler.start()

    time.sleep(1)

    # du_handler.join()
    # message_handler.join()

def generate_f1ap_reset():
    global du_obj
    assert du_obj.du_socket

    reset_f1ap_pdu = F1AP_PDU_Descriptions.F1AP_PDU
    reset_f1ap_pdu.set_val(reset_f1ap_pdu_obj)
    du_obj.du_socket.sctp_send(reset_f1ap_pdu.to_aper(), ppid=socket.htonl(62))

@app.route("/f1ap-proxy/status", methods=["GET"])
def get_proxy_status():
    global is_upgrade_completed
    return {'upgrade_completed': is_upgrade_completed}
# Example: curl -X GET http://localhost:8888/f1ap-proxy/status

@app.route("/f1ap-proxy/cu", methods=["GET"])
def get_cu_connection():
    global cu_pool
    curr_cu = cu_pool.get_current_cu()
    next_cu = cu_pool.get_next_cu()
    if curr_cu:
        return_json = dict()
        return_json["current_cu"] = {"cu_ip": curr_cu.cu_ip, "cu_port": curr_cu.cu_port, "version": curr_cu.version}
        if next_cu:
            return_json["next_cu"] = {"cu_ip": next_cu.cu_ip, "cu_port": next_cu.cu_port, "version": next_cu.version}
        return jsonify(return_json)
    else:
        return {'success': False }, 404
# Example: curl -X GET http://localhost:8888/f1ap-proxy/cu

# Invoked by K8S PostStart hook.
@app.route("/f1ap-proxy/cu", methods=["POST"])
def add_cu_connection():
    global cu_pool
    
    cu_json = request.get_json()
    cu_ip = cu_json["cu_ip"]
    cu_port = cu_json["cu_port"]
    cu_version = cu_json["version"]
    
    print(f"[CMD] Adding CU, {cu_ip}:{cu_port}!")
    cu_socket = sctp.sctpsocket_tcp(socket.AF_INET)
    # let connect to be able to retry several times
    attempt = 0
    while attempt < 5:
        try:
            cu_socket.connect((cu_ip, int(cu_port)))
            break
        except:
            attempt += 1
            time.sleep(5)
    if attempt == 5:
        print(f"Failed to connect to CU {cu_ip}:{cu_port} after 5 attempts.")
        return {'success': False}, 500
    print(f"Connected to CU {cu_ip}:{cu_port}!")
    # TODO: the CU socket creation should be part of the CUPool handling
    # so that things are consistent with how the CU socket is destroyed.
    cu_obj = CUConnectionObject(cu_socket, cu_ip, cu_port, cu_version)
    try:
        cu_pool.add_cu(cu_obj)
        threading.Thread(target=handle_CU_connection, args=(cu_obj,)).start()
    except:
        return {'success': False}, 500
    return {'success': True}, 200
# Example: curl -X POST -H "Content-Type: application/json" -d '{"cu_ip": "192.168.1.1" , "cu_port": "12345", "version": "122"}' http://localhost:8888/f1ap-proxy/cu

# Invoked by K8S PreStop hook.
@app.route("/f1ap-proxy/cu", methods=["DELETE"])
def remove_cu_connection():
    global cu_pool
    global is_upgrade_completed
    is_upgrade_completed = False
    try:
        generate_f1ap_reset()
        cu_pool.retire_current_cu()
    except:
        return {'success': False}, 500
    is_upgrade_completed = True
    return {'success': True}, 200
# curl -X DELETE http://localhost:8888/f1ap-proxy/cu

def start_command_server(cmd_ip: str, cmd_port: int, is_debug: bool):
    app.run(host=cmd_ip, port=cmd_port, debug=is_debug)

# handle SIGTERM
def handle_sigterm(signum, frame):
    print(f"[SIGTERM] Received signal {signum}.")
    sys.exit(0)

import signal
signal.signal(signal.SIGTERM, handle_sigterm)

def main():
    parser = argparse.ArgumentParser(description="SwapRAN F1AP proxy")
    
    # F1AP proxy address
    # NOTE: To the DU, this is the address of the CU.
    parser.add_argument("--proxy-ip", type=str, required=True, help="F1AP proxy IP address")
    parser.add_argument("--proxy-port", type=int, default=38472, help="F1AP proxy port")

    # F1AP proxy command server address
    # NOTE: This interface allows the orchestration framework (e.g., Helm) to interact with the F1AP proxy.
    parser.add_argument("--cmd-ip", type=str, default="0.0.0.0", help="F1AP proxy command server IP address")
    parser.add_argument("--cmd-port", type=int, default=8888, help="F1AP proxy command server port")

    # Debug flag
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    pprint(args)

    proxy_ip = args.proxy_ip
    proxy_port = args.proxy_port

    cmd_ip = args.cmd_ip
    cmd_port = args.cmd_port

    is_debug = args.debug

    threading.Thread(target=lambda: start_f1ap_proxy(proxy_ip, proxy_port, is_debug)).start()
    threading.Thread(target=lambda: start_command_server(cmd_ip, cmd_port, is_debug)).start()

if __name__ == "__main__":
    main()