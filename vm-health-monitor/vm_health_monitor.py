import paramiko
import datetime
import os

# ── Configuration ──────────────────────────────────────────
HOST     = "192.168.56.20"
PORT     = 22
USERNAME = "dn196"
PASSWORD = os.environ.get("VM_PASSWORD")
LOG_DIR  = "reports"
# ───────────────────────────────────────────────────────────


def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)
    return client

def run_command(client, command):
    _, stdout, _ = client.exec_command(command)
    return stdout.read().decode().strip()

def collect_metrics(client):
    metrics = {}
    metrics["hostname"] = run_command(client, "hostname")
    metrics["uptime"] = run_command(client, "uptime -p")
    metrics["memory"] = run_command(client, "free -h | awk '/^Mem/ {print $2}'")
    metrics["cpu_usage"] = run_command(client, "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    metrics["disk_usage"] = run_command(client, "df -h / | awk 'NR==2 {print $3 \" used /\" $2 \" total(\" $5 \" full)\"}'")
    metrics["disk_pct"]   = run_command(client, "df / | awk 'NR==2 {print $5}' | tr -d '%'")
    metrics["cpu_raw"]    = run_command(client, "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    metrics["logged_users"] = run_command(client, "who | wc -l")
    return metrics

def check_status(metrics):
    warnings = []
    try:
        if float(metrics["cpu_raw"]) > 80:
            warnings.append(f"  !! CPU usage is high: {metrics['cpu_raw']}%")
    except ValueError:
        pass
    try:
        if int(metrics["disk_pct"]) > 90:
            warnings.append(f"  !! Disk usage is high: {metrics['disk_pct']}%")
    except ValueError:
        pass
    return warnings

def generate_report(metrics):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    warnings  = check_status(metrics)
    status    = "Normal" if not warnings else "Warning- See Below"

    warning_block = "\n".join(warnings) if warnings else "  None"

    report = f"""
    VM Health Report - {timestamp}
    ---------------------------
    Hostname:     {metrics['hostname']}
    Uptime:       {metrics['uptime']}
    Memory:       {metrics['memory']}
    CPU Usage:    {metrics['cpu_raw']}%
    Disk Usage:   {metrics['disk_usage']}
    Logged Users: {metrics['logged_users']}

    Status: {status}
    Warnings:
{warning_block}
    """
    return report, timestamp

def save_report(report, timestamp):
    os.makedirs(LOG_DIR, exist_ok=True)
    filename = f"{LOG_DIR}/report_{timestamp.replace(':', '-').replace(' ', '_')}.txt"
    with open(filename, "w") as f:
        f.write(report)
    return filename    

def main():
    print("Connecting to VM...")
    client = connect()
    print("Collecting metrics...")
    metrics = collect_metrics(client)
    print("Generating report...")
    report, timestamp = generate_report(metrics)
    print(report)
    print("Saving report...")
    filename = save_report(report, timestamp)
    print(f"Report saved to: {filename}")

if __name__ == "__main__":
    main()
