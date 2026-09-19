import csv
import json
import os
import re
import socket

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_invalid(row):
    if not row["name"].strip():
        return True
    if not row["email"].strip():
        return True
    if not EMAIL_RE.match(row["email"]):
        return True
    if not row["signup_date"].strip():
        return True
    return False

def main():
    completion_index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    shard_path = f"/app/shards/shard_{completion_index}.csv"
    pod_name = os.environ.get("POD_NAME", socket.gethostname())
    node_name = os.environ.get("NODE_NAME", "unknown")

    total_count = 0
    invalid_count = 0
    with open(shard_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_count += 1
            if is_invalid(row):
                invalid_count += 1

    result = {
        "shard_index": completion_index,
        "shard_file": f"shard_{completion_index}.csv",
        "pod_name": pod_name,
        "node_name": node_name,
        "total_rows": total_count,
        "invalid_rows": invalid_count,
    }
    print(f"RESULT_JSON:{json.dumps(result)}")

if __name__ == "__main__":
    main()