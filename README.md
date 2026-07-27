# PythonAutomation
Repo for task automation projects using Python.

# VM health monitor

## Purpose
Collects usage metrics for my Ubuntu Server virtual machine through SSH functionality. Prints these statistics and also saves them to a file.

## Requirements
Requires paramiko to run (pip install paramiko)

## A note on credentials
Password credentials are handled via environment variables rather than being hardcoded.

## How to run
With virtual server running, set your VM password as an environment variable in powershell:
`$env:VM_PASSWORD = "your_password"`
And run the program:
`python vm_health_monitor.py`
