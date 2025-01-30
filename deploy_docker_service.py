import os
import subprocess
import stat
import sys

service_path = "/etc/systemd/system/dockerot.service"
script_path = "/dockerot.sh"

service_content = """
[Unit]
Description=Run my script at startup and shutdown
DefaultDependencies=no
After=network.target
Before=shutdown.target reboot.target halt.target

[Service]
Type=oneshot  
RemainAfterExit=yes
ExecStart=/dockerot.sh start
ExecStop=/dockerot.sh stop

[Install]
WantedBy=multi-user.target
"""

script_content = """#!/bin/bash

if [ "$1" == "start" ]; then
    echo "System is starting up!" >> /var/log/dockerot.log
    # Add your startup commands here
elif [ "$1" == "stop" ]; then
    echo "System is shutting down!" >> /var/log/dockerot.log
    # Add your shutdown commands here
fi
"""

def create_service():
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
        print(f"Service file created at {service_path}")
    except Exception as e:
        print(f"Error creating service file: {e}")
        
def create_script():
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        # Make the script executable
        os.chmod(script_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        print(f"Script file created and made executable at {script_path}")
    except Exception as e:
        print(f"Error creating script file: {e}")

def enable_and_start_service():
    try:
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "dockerot.service"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "dockerot.service"], check=True)
        print("Service enabled and started.")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling or starting the service: {e}")

def check_logs():
    try:
        subprocess.run(["journalctl", "-u", "dockerot.service", "--no-pager", "--reverse"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving logs: {e}")

def check_sudo():
    if os.geteuid() != 0:
        print("This script must be run with sudo!")
        sys.exit(1)
    else:
        print(f"UID : {os.geteuid()}")

def setup_service():
    check_sudo()
    create_service()
    create_script()
    enable_and_start_service()
    check_logs()

if __name__ == "__main__":
    setup_service()