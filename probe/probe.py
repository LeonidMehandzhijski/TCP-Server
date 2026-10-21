import argparse
import socket
import sqlite3
import sys
import time
from datetime import datetime, timezone

DB_FILE = "monitor.db"
SOURCE_HOST = socket.gethostname()


def setup_db():
    db = sqlite3.connect(DB_FILE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            source_host TEXT NOT NULL,
            target TEXT NOT NULL,
            check_type TEXT NOT NULL,
            ok INTEGER NOT NULL,
            latency_ms REAL,
            loss_pct REAL,
            jitter_ms REAL,
            error TEXT
        )
    """)
    db.commit()
    return db


def check_tcp_echo(host, port):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=2) as s:
            s.sendall(b"ping")
            reply = s.recv(1024)
        if reply != b"ping":
            return {"ok": False, "error": "bad reply"}
        ms = (time.perf_counter() - start) * 1000
        return {"ok": True, "latency_ms": ms}
    except OSError as e:
        return {"ok": False, "error": str(e)}


def check_udp_echo(host, port, count=10, timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    rtts = []
    lost = 0
    error = None
    for seq in range(count):
        payload = str(seq).encode()
        start = time.perf_counter()
        sock.sendto(payload, (host, port))
        try:
            reply, _ = sock.recvfrom(1024)
            if reply == payload:
                rtts.append((time.perf_counter() - start) * 1000)
            else:
                lost += 1
        except socket.timeout:
            lost += 1
            error = "timeout"
        except ConnectionResetError:
            lost += 1
            error = "port unreachable"
        time.sleep(0.2)
    sock.close()

    result = {"ok": len(rtts) > 0, "loss_pct": lost / count * 100, "error": error}
    if rtts:
        result["latency_ms"] = sum(rtts) / len(rtts)
        diffs = [abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))]
        result["jitter_ms"] = sum(diffs) / len(diffs) if diffs else 0.0
    return result


def save(db, host, port, check_type, r):
    db.execute(
        "INSERT INTO checks (ts, source_host, target, check_type, ok, "
        "latency_ms, loss_pct, jitter_ms, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), SOURCE_HOST, f"{host}:{port}",
         check_type, int(r["ok"]), r.get("latency_ms"), r.get("loss_pct"),
         r.get("jitter_ms"), r.get("error")),
    )
    db.commit()


host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

parser = argparse.ArgumentParser(description="Network probe")
parser.add_argument("host", nargs="?", default="127.0.0.1")
parser.add_argument("--checks", nargs="+", choices=["tcp", "udp"],
                    default=["tcp", "udp"],
                    help="which checks to run (default: all)")
args = parser.parse_args()

db = setup_db()
all_ok = True

if "tcp" in args.checks:
    r = check_tcp_echo(args.host, 5000)
    save(db, args.host, 5000, "tcp_echo", r)
    print("TCP:", r)
    all_ok = all_ok and r["ok"]

if "udp" in args.checks:
    r = check_udp_echo(args.host, 5001)
    save(db, args.host, 5001, "udp_echo", r)
    print("UDP:", r)
    all_ok = all_ok and r["ok"]

db.close()
sys.exit(0 if all_ok else 1)