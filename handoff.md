# Handoff
**Last updated:** 2026-10-23
**Current project / stage:** The Platform, Stage A1: network connectivity monitor (TCP/UDP echo servers as probe targets, hosted on AWS next)

**Done so far:**
- Repo folder currently named `TCP and UDP Server`. Layout: `servers/` (deployed code), `tools/` (test clients + report), `probe/` (the monitor).
- `servers/tcp_echo.py`: threaded TCP echo server, port 5000, one thread per caller. Tested PC -> laptop over the hotspot (no client isolation).
- `servers/udp_echo.py`: UDP echo server, port 5001, no connection state.
- `tools/tcp_client.py`, `tools/udp_client.py`: throwaway test clients (UDP client separates timeout from ConnectionResetError).
- `probe/probe.py`: runs TCP and/or UDP checks (`--checks tcp udp`, optional host argument), writes one row per check to SQLite `monitor.db`, exit code 0 only if the checks that ran passed. UDP check sends 10 sequence-numbered packets and records avg latency, loss %, jitter.
- `tools/report.py`: GROUP BY summary per host and check type.
- Schema (the contract for Stage B): `checks(id, ts, source_host, target, check_type, ok, latency_ms, loss_pct, jitter_ms, error)`. `ts` is UTC ISO 8601. `monitor.db` is gitignored.
- AWS account created on the Free plan: root MFA, daily-use IAM user with MFA, budget alert set. Region selector issue: user could not select a region (see open questions).

**In progress:** diagnosing high UDP loss between the Fedora laptop (probe) and the Windows PC (echo server) over the phone hotspot: about 60-70% loss and up to ~275 ms jitter, while ICMP ping between the same machines shows 0% loss at 6-12 ms.

**Next steps:**
1. Finish the UDP diagnosis (count `Got` lines on the PC server during one probe run to see whether packets are lost inbound or on the reply; then run the probe against the PC's own LAN IP; then swap roles with the server on the laptop).
2. Step 11: launch one small EC2 instance by hand in the console, SSH in, run both echo servers as systemd services, open TCP 5000 and UDP 5001 in the security group.
3. Probe the EC2 target from the hotspot, then rebuild the instance with Terraform (destroy and recreate).

**Decisions made and why:**
- Echo servers are the A1 probe targets: ICMP is unreliable on mobile links, and UDP echo with sequence numbers measures loss and jitter.
- One probe program with selectable checks (`--checks`), not one script per protocol: shared DB code, different schedules via the command line.
- The loop lives outside the script (systemd timer on Fedora). Scheduling is deferred until the servers are on AWS, so only the probe machine has to be on.
- AWS is the remote vantage point. Do it by hand once, then Terraform. Azure later with the same concepts.
- A2 (port scanner against a Docker lab network) is deferred until A1 is done. Monitor and scanner use separate SQLite files.
- Stage B (dashboard) is a separate repo and reads the SQLite file read-only.
- Hotspot is metered: keep probes tiny, pull images and packages sparingly.

**Known issues / open questions:**
- UDP loss/jitter cause unknown. `nmcli ... powersave = 0 (default)` does NOT prove Wi-Fi power saving is off, since it means "use the driver default"; check with `iw dev wlp3s0 get power_save`.
- TCP avg latency in the report is 181 ms across 7 runs although a single run earlier was 17 ms: list individual rows to find the outliers.
- Possible bug: `check_udp_echo` does not catch an `OSError` from `sendto` when the network is completely down (untested).
- Both machines may report the same `source_host` (laptop hostname is `CicadaKatz`); check the PC's hostname and add a `--name` option if they match.
- AWS region: user could not select a region in the console. Find out which region is shown; any region works for learning, but a distant one inflates latency numbers.

**Where I am as a learner:**
- Understood: sockets, bind/listen/accept, why a single-threaded server blocks, threads per client, TCP vs UDP semantics, why UDP loss is only detected by timeout, SQL GROUP BY summaries, exit codes.
- Typed in but only partly understood: list comprehensions, `try/except` with specific exceptions, f-strings and parameterized SQL, `argparse` (used before in LogAnalyzer).
- New and untouched: Terraform, systemd timers, AWS networking (security groups, VPC), IAM details.