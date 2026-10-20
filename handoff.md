# Handoff
**Last updated:** 2026-10-20
**Current project / stage:** Stage A1 echo servers (probe targets for the monitor)
**Done so far:** tcp_echo.py (threaded, multi-caller) and tcp_client.py, tested PC -> laptop over the phone hotspot (no client isolation)
**In progress:** udp_echo.py / udp_client.py (local test first)
**Next steps:** 1) finish UDP echo, test across machines 2) probe_client.py writing latency/loss/jitter to SQLite (monitor.db) 3) manual EC2 deployment in eu-central-1
**Decisions made and why:** echo servers are the A1 probe targets (ICMP is unreliable on mobile links); AWS is the remote vantage point; A2 lab scanner deferred; monitor and scanner use separate SQLite files
**Known issues / open questions:** hotspot has a data cap, keep probes tiny; UDP loss detection is timeout-based
**Where I am as a learner:** understands sockets, bind/listen/accept, why one-at-a-time servers block, threads per client; still new to try/except and sys.argv