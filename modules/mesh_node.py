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
KNOWN_MESH_PORTS = [8000, 8765, 8766, 8767, 8768]
ssl_ctx = ssl._create_unverified_context()

active_peers_lock = threading.Lock()
active_peers = {} # key -> peer_info

def register_peer(ip, username, port=8765, app="Revision-App", is_self=False, power=15.0):
    with active_peers_lock:
        key = f"{ip}:{port}"
        active_peers[key] = {
            "ip": ip,
            "port": port,
            "app": app,
            "username": username or f"Peer_{ip.replace('.', '_')}",
            "power": power,
            "last_seen": time.time(),
            "is_self": is_self
        }

def cleanup_stale_peers():
    with active_peers_lock:
        now = time.time()
        to_del = [k for k, v in active_peers.items() if not v.get("is_self") and (now - v["last_seen"]) > 60]
        for k in to_del:
            del active_peers[k]

class MeshStatusHandler(BaseHTTPRequestHandler):
    server_version = "RevNetworkP2P/2.0"

    def do_GET(self):
        cleanup_stale_peers()
        with active_peers_lock:
            peers_list = list(active_peers.values())
        
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
            "power_score": getattr(self.server, "power_score", 30.0),
            "active_peers_count": len(peers_list),
            "peers": peers_list
        }
        self.wfile.write(json.dumps(resp).encode("utf-8"))

    def log_message(self, format, *args):
        pass

def _run_udp_broadcast(port: int, app_name: str, node_id: str, power_score: float):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    broadcast_targets = [("<broadcast>", UDP_DISCOVERY_PORT), ("127.0.0.1", UDP_DISCOVERY_PORT), ("26.255.255.255", UDP_DISCOVERY_PORT)]
    
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
            for target in broadcast_targets:
                try:
                    s.sendto(msg, target)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(8)

def _run_udp_listener(my_port: int, my_node_id: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    try:
        s.bind(("", UDP_DISCOVERY_PORT))
        while True:
            try:
                data, addr = s.recvfrom(2048)
                payload = json.loads(data.decode("utf-8"))
                if payload.get("magic") == "REV_P2P_V2":
                    peer_ip = addr[0]
                    peer_port = payload.get("port", 8765)
                    peer_app = payload.get("app", "Revision-App")
                    peer_power = payload.get("power_score", 15.0)
                    peer_nid = payload.get("node_id", "")
                    if peer_nid != my_node_id and not (peer_ip in ["127.0.0.1"] and peer_port == my_port):
                        register_peer(
                            ip=peer_ip,
                            username=f"{peer_app} Pilot",
                            port=peer_port,
                            app=peer_app,
                            is_self=False,
                            power=peer_power
                        )
            except Exception:
                pass
    except Exception:
        pass

def _probe_local_ring(my_port: int, my_node_id: str):
    time.sleep(2)
    hosts_to_probe = ["127.0.0.1", "26.68.132.89"]

    while True:
        for host in hosts_to_probe:
            for p in KNOWN_MESH_PORTS:
                if host == "127.0.0.1" and p == my_port:
                    continue
                try:
                    url = f"http://{host}:{p}/api/status"
                    req = Request(url, headers={"User-Agent": "RevMeshProber/1.0"})
                    with urlopen(req, timeout=0.8) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                            p_app = data.get("app") or ("Origin Web Gateway" if p == 8000 else "Revision Node")
                            p_power = float(data.get("power_score", 20.0))
                            p_id = data.get("node_id", "")
                            if p_id != my_node_id:
                                register_peer(
                                    ip=host,
                                    username=f"{p_app} [Local Mesh]",
                                    port=p,
                                    app=p_app,
                                    is_self=False,
                                    power=p_power
                                )
                except Exception:
                    pass
        time.sleep(6)

def _run_heartbeat_loop(origin_url: str, node_id: str, app_name: str, port: int, power_score: float):
    endpoints = [
        "http://127.0.0.1:8000",
        "http://26.68.132.89:8000",
        origin_url.rstrip('/')
    ]

    payload = json.dumps({
        "node_id": node_id,
        "app": app_name,
        "port": port,
        "role": "DDoS-Shielded Community Mesh Relay",
        "power_score": power_score
    }).encode("utf-8")

    while True:
        for base_ep in endpoints:
            try:
                reg_url = f"{base_ep}/api/register-node"
                req = Request(reg_url, data=payload, headers={"Content-Type": "application/json"})
                with urlopen(req, timeout=4, context=ssl_ctx if reg_url.startswith("https") else None) as resp:
                    if resp.status == 200:
                        res_data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        peers = res_data.get("peers") or res_data.get("nodes") or []
                        for peer in peers:
                            p_nid = peer.get("node_id")
                            if p_nid and p_nid != node_id:
                                p_ip = peer.get("ip") or peer.get("client_ip") or "127.0.0.1"
                                p_port = int(peer.get("port", 8765))
                                p_app = peer.get("app", "Revision-App")
                                p_power = float(peer.get("power_score", 15.0))
                                register_peer(
                                    ip=p_ip,
                                    username=f"{p_app} Pilot",
                                    port=p_port,
                                    app=p_app,
                                    is_self=False,
                                    power=p_power
                                )
                        break
            except Exception:
                pass
        time.sleep(12)

def start_mesh_node(app_name: str = "Revision-Ai", port: int = 0, origin_url: str = ORIGIN_TRACKER_URL):
    """
    Starts the transparent, low-resource mesh relay node in a daemon thread.
    Consumes < 15MB RAM and near-zero CPU.
    """
    if port == 0:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('0.0.0.0', 8766))
            port = 8766
        except Exception:
            s.bind(('0.0.0.0', 0))
            port = s.getsockname()[1]
        finally:
            s.close()

    cores = os.cpu_count() or 4
    power_score = round(cores * 2.5 + 10.0, 1)
    node_id = f"relay-{app_name.lower().replace(' ', '-')[:12]}-{int(time.time()*1000) % 100000}"

    register_peer("127.0.0.1", f"{app_name} (Self)", port=port, app=app_name, is_self=True, power=power_score)

    print(f"\n[REV MESH] ===================================================")
    print(f"[REV MESH] Interconnected Community P2P Node Active (Eco Mode)")
    print(f"[REV MESH] Node ID: {node_id} | App: {app_name}")
    print(f"[REV MESH] Port: {port} | Power Score: {power_score}")
    print(f"[REV MESH] ===================================================\n")

    try:
        httpd = ThreadingHTTPServer(('0.0.0.0', port), MeshStatusHandler)
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

        threading.Thread(
            target=_run_udp_listener,
            args=(port, node_id),
            daemon=True
        ).start()

        threading.Thread(
            target=_probe_local_ring,
            args=(port, node_id),
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
