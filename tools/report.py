import sqlite3

db = sqlite3.connect("monitor.db")
rows = db.execute("""
    SELECT source_host, check_type,
           COUNT(*) AS runs,
           ROUND(AVG(latency_ms), 2) AS avg_latency,
           ROUND(AVG(loss_pct), 1) AS avg_loss,
           ROUND(MAX(jitter_ms), 2) AS max_jitter,
           SUM(1 - ok) AS failures
    FROM checks
    GROUP BY source_host, check_type
""").fetchall()

print("host | type | runs | avg_ms | avg_loss% | max_jitter | failures")
for r in rows:
    print(" | ".join(str(x) for x in r))
db.close()