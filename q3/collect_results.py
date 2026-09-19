"""
collect_results.py
Collects RESULT_JSON lines from every pod of the shard-validation-job
via the Kubernetes API, reading pod logs directly (not a shared volume).
"""
import json
import re
import sys

from kubernetes import client, config

RESULT_LINE_RE = re.compile(r"RESULT_JSON:(\{.*\})")


def load_kube_config():
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()


def collect(job_name, namespace="default"):
    load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(
        namespace=namespace, label_selector=f"job-name={job_name}"
    )
    if not pods.items:
        print(f"No pods found for job '{job_name}'.", file=sys.stderr)
        return []

    results = []
    for pod in pods.items:
        pod_name = pod.metadata.name
        log = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
        match = RESULT_LINE_RE.search(log)
        if not match:
            print(f"WARNING: no RESULT_JSON found in logs for {pod_name}", file=sys.stderr)
            continue
        results.append(json.loads(match.group(1)))

    results.sort(key=lambda r: r["shard_index"])
    return results


def main():
    results = collect("shard-validation-job")

    print(f"{'shard':<6} {'pod_name':<28} {'node':<14} {'total':<7} {'invalid':<7}")
    print("-" * 70)
    for r in results:
        print(
            f"{r['shard_index']:<6} {r['pod_name']:<28} {r['node_name']:<14} "
            f"{r['total_rows']:<7} {r['invalid_rows']:<7}"
        )

    total_invalid = sum(r["invalid_rows"] for r in results)
    print("-" * 70)
    print(f"Total invalid rows across all 8 shards: {total_invalid}")


if __name__ == "__main__":
    main()