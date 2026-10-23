# TCP-and-UDP echo servers

I'm building two small echo servers to learn Python, sockets and DevOps stuff. It sends TCP and UDP messages to two echo servers and writes down how long the replies took and how many never came back.

## What's in here

```
servers/
  tcp_echo.py     TCP echo server, port 5000, one thread per caller
  udp_echo.py     UDP echo server, port 5001
tools/
  tcp_client.py   quick test client for the TCP server
  udp_client.py   quick test client for the UDP server
  report.py       prints a summary of what's in the database
probe/
  probe.py        the actual monitor
```

No pip install needed, it's all standard library. Python 3 only.

## Running it

Start the servers, each in its own terminal:

```
python servers/tcp_echo.py
python servers/udp_echo.py
```

On Windows use `py` instead of `python`.

Then run the probe, on the same machine or another one on the same network:

```
python probe/probe.py                          # both checks against 127.0.0.1
python probe/probe.py 192.168.1.50             # both checks against another machine
python probe/probe.py 192.168.1.50 --checks udp
python probe/probe.py --checks tcp
```

The exit code is 0 if every check that ran passed. The exit code is 1 otherwise, so it can be scheduled later without changing anything.

To see what it recorded:

```
python tools/report.py
```

If it works on localhost but not from another machine, it might be the firewall. I personally tested it on a Windows PC and a Fedora KDE Plasma laptop I have. They communicated well with no problem. No ports needed to be open.
## What it measures

- **TCP check:** connects, sends a message, waits for the echo, and times the whole thing.
- **UDP check:** sends 10 numbered packets, 0.2 seconds apart, and records average round trip time, loss percentage, and jitter.

## The database

Results go into a SQLite file called `monitor.db`, one row per check. This table is the contract for the dashboard later.

| column      | what it is                                 |
|-------------|--------------------------------------------|
| ts          | timestamp when the check ran, UTC          |
| source_host | which machine ran the probe                |
| target      | what it checked, like `10.0.0.5:5000`      |
| check_type  | `tcp_echo` or `udp_echo`                   |
| ok          | 1 if it worked, 0 if it didnt              |
| latency_ms  | round trip time (average for UDP)          |
| loss_pct    | UDP only, how many packets never came back |
| jitter_ms   | UDP only                                   |
| error       | what went wrong, if anything               |

## Things I ran into

- When I first started making the TCP Server it could only talk to one client. A second client would just freeze until the first one hung up, because the server was stuck waiting on the first connection to stop. This is where I learned about threads, now each connection has its own thread.
- First major-ish problem I encountered was stopping the UDP server and then running the client gave a `ConnectionResetError` on Windows, while on Linux it just gave the response that no one was listening... Windows turns the nobody is listening reply into an error, but Linux doesn't, it just times out. So the probe treats both as a failure and stores which one it saw.
- For some reason while probing from my laptop to my PC, all of a sudden the UDP loss numbers looked way too high while ping showed 0% loss, I counted the packets on the server and all 10 arrived, so the loss wasn't real. I'm still sorting out whether it's a bug in how my probe matches replies. I'll update this once I know. Theoretically it could be because of a lot of things. Needs more testing.
- One thing I learned about how to better future-proof your code is, when it came down to actually probing it would always run both the udp and tcp checks. But maybe I just wanted to test one. So because I learned about argparse in my LogAnalyzer project I was able to use that to make --check udp or tcp. Why I say this was for future proofing is because I was ready to just make them seperate scripts. But that would be reusing the same code which wouldn't be very efficient.
- There is also something I learned from a OpenAI workshop & hackathon that was organized recently that I used here. As I am also using AI to shepherd me through this. Mainly Claude Code but when I run out of tokens I use Codex. The man handling the workshop kept talking about how to use AI Agents the best. Something that stuck with me was the file structure that was very important. But also handoff.md. Makes switching from one agent to the next much easier.

## Where this is going

- [x] TCP and UDP echo servers
- [x] Probe that writes to SQLite
- [x] Test between two machines over a phone hotspot
- [ ] Host the servers on AWS (EC2, Frankfurt) and probe them from the hotspot
- [ ] Rebuild that setup with Terraform
- [ ] Run the probe on a timer (systemd) instead of by hand
- [ ] Dashboard (separate repo)