import random
import csv
import os

random.seed(42)

NUM_SHARDS = 8
ROWS_PER_SHARD = 50

FIRST_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
LAST_NAMES = ["Smith", "Jones", "Brown", "Taylor", "Wilson", "Davies", "Evans", "Thomas", "Roberts", "Walker"]
DOMAINS = ["example.com", "mail.com", "test.org", "company.net"]
COUNTRIES = ["IN", "US", "UK", "DE", "AU", "CA"]

MALFORMED_EMAIL_PATTERNS = [
    lambda local, domain: f"{local}{domain}",                     # missing @
    lambda local, domain: f"{local}@",                            # missing domain
    lambda local, domain: f"@{domain}",                           # missing local part
    lambda local, domain: f"{local}@{domain.replace('.', '')}",   # missing dot
]

os.makedirs("shards", exist_ok=True)
shard_invalid_counts = {}

for shard_idx in range(NUM_SHARDS):
    rows = []
    invalid_count = 4 + shard_idx  # distinct, known count per shard
    invalid_row_indices = set(random.sample(range(ROWS_PER_SHARD), invalid_count))

    for row_idx in range(ROWS_PER_SHARD):
        user_id = f"S{shard_idx}-U{row_idx:03d}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        local = name.lower().replace(" ", ".")
        domain = random.choice(DOMAINS)
        email = f"{local}@{domain}"
        signup_date = f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        country = random.choice(COUNTRIES)

        if row_idx in invalid_row_indices:
            fault = random.choice(["bad_email", "missing_email", "missing_name", "missing_date"])
            if fault == "bad_email":
                email = random.choice(MALFORMED_EMAIL_PATTERNS)(local, domain)
            elif fault == "missing_email":
                email = ""
            elif fault == "missing_name":
                name = ""
            elif fault == "missing_date":
                signup_date = ""

        rows.append([user_id, name, email, signup_date, country])

    shard_invalid_counts[shard_idx] = invalid_count

    with open(f"shards/shard_{shard_idx}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "name", "email", "signup_date", "country"])
        writer.writerows(rows)

print("Ground truth (for your own verification against pod output later):")
for k, v in shard_invalid_counts.items():
    print(f"  shard_{k}.csv -> {v} invalid rows")