import subprocess
import datetime
import re

# Get date 30 days ago
threshold_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

# Read the IP addresses and dates from the text file
file_path = "/root/firewall/banipufw/banip.txt"
ip_dates = {}
rule_changes = False  # Track if any changes were made

with open(file_path, 'r') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 2 and parts[1].count('-') == 2:
            ip, date = parts[0], parts[1]
            ip_dates[ip] = date

# Fetch current ufw rules and save to a temporary file
subprocess.run(["ufw", "status", "numbered"], stdout=open('/tmp/current_ufw_rules.txt', 'w'))

# Read from the temporary file for rule processing
with open('/tmp/current_ufw_rules.txt', 'r') as file:
    rule_lines = file.readlines()

# Function to check rule existence
def rule_exists(ip):
    pattern = re.compile(f"(DENY IN|REJECT IN).*{ip}")
    return any(pattern.search(line) for line in rule_lines)

# Remove outdated rules
for ip, date in ip_dates.items():
    if date < threshold_date:
        for line in rule_lines:
            if re.search(f"(DENY IN|REJECT IN).*{ip}", line):
                rule_number = re.findall(r'\[\s*(\d+)\s*\]', line)[0]
                subprocess.run(["ufw", "delete", rule_number], input="y\n".encode(), check=True)
                print(f"Removed expired rule for IP '{ip}' from {date}.")
                rule_changes = True

# Add new IP ban rules avoiding duplicates
for ip, date in ip_dates.items():
    if date >= threshold_date and not rule_exists(ip):
        subprocess.run(["ufw", "insert", "1", "deny", "from", ip, "to", "any"], check=True)
        print(f"Added new rule for IP '{ip}'.")
        rule_changes = True

if not rule_changes:
    print("No changes required. All rules are up to date.")

# Optionally, you can also log the updated rule list after changes
subprocess.run(["ufw", "status", "numbered"], stdout=open('/tmp/updated_ufw_rules.txt', 'w'))
