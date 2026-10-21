| Column | Meaning |
| :--- | :--- |
| `ts` | when the check ran |
| `source_host` | which machine ran the check |
| `target` | what it checked, e.g. `10.21.110.143:5000` |
| `check_type` | `tcp_echo` (later `udp_echo`) |
| `ok` | 1 if it worked, 0 if not |
| `latency_ms` | how long the round trip took (empty on failure) |
| `error` | what went wrong (empty on success) |