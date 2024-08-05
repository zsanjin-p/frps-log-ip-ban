# FRPS Log IP Ban Tool

This tool is designed to enhance security for services exposed through FRP (Fast Reverse Proxy) by automatically banning IPs that attempt brute-force attacks or other suspicious activities on specified services like Windows Remote Desktop.

## Features

- **Log Monitoring:** Monitors FRPS logs for failed login attempts.
- **Auto IP Ban:** Automatically bans IPs exceeding a certain number of failed attempts within a specified time frame.
- **Whitelist Support:** Allows specifying IP addresses that should never be banned.
- **Scheduled Unban:** Automatically unbans IPs after a certain period.
- **Integration with Firewall:** Works with both Windows Firewall and UFW (on Linux).

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/zsanjin-p/frps-log-ip-ban
   ```

2. Navigate to the project directory:
   ```
   cd frps-log-ip-ban
   ```

3. Install dependencies:
   ```
   # No specific dependencies mentioned, ensure you have Python and relevant firewall configurations.
   ```

## Configuration

1. Update the `.env` file with your specific settings:
   ```
   LOG_FILE_PATH=C:\Path\To\Your\frps.log
   TARGET_NAMES=service1,service2
   WHITELIST=ip1,ip2
   BAN_FILE_PATH=C:\Path\To\banip.txt
   EXECUTE_PATH=C:\Path\To\banip.ps1
   CHECK_INTERVAL=5
   THRESHOLD_COUNT=5
   ```

2. Adjust the firewall script (`banip.ps1` for Windows, `banip.py` for Linux) to point to the correct location of your blacklist file and set the ban duration.

## Usage

Run the main script to start monitoring the logs and banning IPs:

```
python frpbanip.py
```

## Automation

### Linux

Create a systemd service to run the script at startup:

```
sudo nano /etc/systemd/system/frpbanip.service
```

Add the following configuration:

```
[Unit]
Description=FRP Log Ban IP Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/frpbanip.py
WorkingDirectory=/path/to
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```
sudo systemctl enable frpbanip
sudo systemctl start frpbanip
```

### Windows

Create a batch file to run the script at startup and use Task Scheduler to add the batch file as a startup task.

## Contributing

Feel free to fork the project, submit pull requests, or star the repository if you find it helpful!

## License

Specify your license or state that the project is unlicensed.

