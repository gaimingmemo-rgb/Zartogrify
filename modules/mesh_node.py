"""
REV NETWORK // COMMUNITY P2P MESH RELAY NODE
An interconnected, low-resource background micro-relay that powers
decentralized community peer discovery, local mesh networking, and shared hosting.
"""

import os
import sys
import json
import time
import ssl
import socket
import threading
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ORIGIN_TRACKER_URL = os.environ.get("REV_ORIGIN_URL", "https://rev-network.ddns.net:8000")
UDP_DISCOVERY_PORT = 8769
ssl_ctx = ssl._create_unverified_context()

class MeshStatusHandler(BaseHTTPRequestHandler):
    server_version = "RevNetworkP2P/2.0"

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        resp = {
            "status": "online",
            "role": "community_edge_relay",
            "app": getattr(self.server, "app_name", "Revision-Ai"),
            "node_id": getattr(self.server, "node_id", "unknown"),
            "port": getattr(self.server, "server_port", 8766),
            "origin": ORIGIN_TRACKER_URL,
            "eco_mode": True,
            "power_score": getattr(self.server, "power_score", 30.0)
        }
        self.wfile.write(json.dumps(resp).encode("utf-8"))

    def log_message(self, format, *args):
        pass

def _run_udp_broadcast(port: int, app_name: str, node_id: str, power_score: float):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        try:
            msg = json.dumps({
                "magic": "REV_P2P_V2",
                "app": app_name,
                "node_id": node_id,
                "port": port,
                "power_score": power_score,
                "time": time.time()
            }).encode("utf-8")
            s.sendto(msg, ("<broadcast>", UDP_DISCOVERY_PORT))
        except Exception:
            pass
        time.sleep(8)

def _run_heartbeat_loop(origin_url: str, node_id: str, app_name: str, port: int, power_score: float):
    endpoint = f"{origin_url.rstrip('/')}/api/register-node"
    endpoints = [endpoint, "http://127.0.0.1:8000/api/register-node"]

    payload = json.dumps({
        "node_id": node_id,
        "app": app_name,
        "port": port,
        "role": "Community Mesh Relay & P2P Node",
        "power_score": power_score
    }).encode("utf-8")

    while True:
        for ep in endpoints:
            try:
                req = Request(ep, data=payload, headers={"Content-Type": "application/json"})
                with urlopen(req, timeout=4, context=ssl_ctx if ep.startswith("https") else None) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                pass
        time.sleep(20)

def start_mesh_node(app_name: str = "Revision-Ai", port: int = 0, origin_url: str = ORIGIN_TRACKER_URL):
    """
    Starts the transparent, low-resource mesh relay node in a daemon thread.
    Consumes < 15MB RAM and near-zero CPU.
    """
    if port == 0:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('127.0.0.1', 8766))
            port = 8766
        except Exception:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        finally:
            s.close()

    cores = os.cpu_count() or 4
    power_score = round(cores * 2.5 + 10.0, 1)
    node_id = f"relay-{app_name.lower().replace(' ', '-')[:12]}-{int(time.time()*1000) % 100000}"

    print(f"\n[REV MESH] ===================================================")
    print(f"[REV MESH] Interconnected Community P2P Node Active (Eco Mode)")
    print(f"[REV MESH] Node ID: {node_id} | App: {app_name}")
    print(f"[REV MESH] Local Port: {port} | Power Score: {power_score}")
    print(f"[REV MESH] ===================================================\n")

    try:
        httpd = ThreadingHTTPServer(('127.0.0.1', port), MeshStatusHandler)
        httpd.app_name = app_name
        httpd.node_id = node_id
        httpd.server_port = port
        httpd.power_score = power_score

        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        threading.Thread(
            target=_run_heartbeat_loop,
            args=(origin_url, node_id, app_name, port, power_score),
            daemon=True
        ).start()

        threading.Thread(
            target=_run_udp_broadcast,
            args=(port, app_name, node_id, power_score),
            daemon=True
        ).start()

        return node_id
    except Exception as e:
        print(f"[REV MESH] Notice: Could not bind relay server: {e}")
        return None

if __name__ == "__main__":
    start_mesh_node(app_name="Revision-Ai")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
