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
            return False, None, "bad reply"
        ms = (time.perf_counter() - start) * 1000
        return True, ms, None
    except OSError as e:
        return False, None, str(e)


host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = 5000

db = setup_db()
ok, latency, error = check_tcp_echo(host, port)

db.execute(
    "INSERT INTO checks (ts, source_host, target, check_type, ok, latency_ms, error) "
    "VALUES (?, ?, ?, ?, ?, ?, ?)",
    (datetime.now(timezone.utc).isoformat(), SOURCE_HOST, f"{host}:{port}",
     "tcp_echo", int(ok), latency, error),
)
db.commit()
db.close()

print("OK" if ok else f"FAILED: {error}", f"latency={latency}")
sys.exit(0 if ok else 1)