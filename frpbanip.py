import os
import re
import subprocess
import ipaddress
import logging
from datetime import datetime, timedelta
from datetime import time as dt_time  # 重命名以避免冲突
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from time import sleep  # 直接导入sleep
from collections import defaultdict  # 用于计数IP出现次数

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置日志目录和文件
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_name = os.path.join(log_directory, 'log_monitor.log')

# 设置日志和控制台输出
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 使用 TimedRotatingFileHandler 进行日志管理
log_file_handler = TimedRotatingFileHandler(
    log_file_name,
    when='midnight',
    interval=1,
    backupCount=7,  # 保留7天的日志文件
    encoding='utf-8',
    atTime=dt_time(0, 0, 0)  # 确保午夜时切换日志文件
)
log_file_handler.suffix = "%Y-%m-%d.log"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 读取环境变量
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'C:\\Users\\Administrator\\Desktop\\frp\\frps.log')
TARGET_NAMES = os.getenv('TARGET_NAMES', '').split(',')
WHITELIST = os.getenv('WHITELIST', '').split(',')
BAN_FILE_PATH = os.getenv('BAN_FILE_PATH', 'C:\\Users\\Administrator\\Desktop\\banip\\frplog\\ban.txt')
EXECUTE_PATH = os.getenv('EXECUTE_PATH', 'C:\\Users\\Administrator\\Desktop\\banip\\frplog\\banip.ps1')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))  # minutes
THRESHOLD_COUNT = int(os.getenv('THRESHOLD_COUNT', '5'))  # 触发禁用IP的次数阈值


def check_ip_whitelisted(ip):
    try:
        for network in WHITELIST:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(network, strict=False):
                logger.info(f"Whitelisted IP: {ip}")
                return True
    except ValueError as e:
        logger.error(f"Invalid IP address or network: {e}")
    return False


def execute_script(ip):
    script_extension = os.path.splitext(EXECUTE_PATH)[-1].lower()
    if script_extension == '.ps1':
        command = ["powershell.exe", "-File", EXECUTE_PATH, ip]
    elif script_extension == '.py':
        # 假设Python脚本需要以命令行参数的形式接收IP地址
        command = ["python", EXECUTE_PATH, ip]
    else:
        command = [EXECUTE_PATH, ip]

    try:
        subprocess.run(command, check=True)
        logger.info(f"Executed script for IP {ip}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute script for IP {ip}: {e}")


def update_ban_list(ip):
    today_date = datetime.now().strftime("%Y-%m-%d")
    found = False
    updated_content = []

    # Reading the entire file and updating the memory copy
    if os.path.exists(BAN_FILE_PATH):
        with open(BAN_FILE_PATH, 'r') as file:
            lines = file.readlines()

        for line in lines:
            # Skip empty lines and malformed entries
            line = line.strip()
            if not line:
                logger.debug("Skipped empty line.")
                continue

            try:
                file_ip, file_date = line.split()
            except ValueError:
                logger.warning(f"Malformed line skipped: {line}")
                continue

            if file_ip == ip:
                updated_content.append(f"{ip}   {today_date}\n")  # Update the date for existing IP
                found = True
            else:
                updated_content.append(f"{file_ip}   {file_date}\n")  # Ensure proper format with newline

    if not found:
        updated_content.append(f"{ip}   {today_date}\n")  # Add new IP with the current date

    # Rewriting the updated content to the file
    with open(BAN_FILE_PATH, 'w') as file:
        file.writelines(updated_content)

    if found:
        logger.info(f"Updated existing IP {ip} in ban list with new date {today_date}.")
    else:
        logger.info(f"Added new IP {ip} to ban list with date {today_date}.")
    execute_script(ip)


def analyze_log():
    now = datetime.now()
    time_threshold = now - timedelta(minutes=CHECK_INTERVAL)
    logger.info(f"Analyzing logs after {time_threshold}")

    pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[.*?\] \[.*?\] \[.*?\] \[(.*?)\] .*? \[(.*?):')

    ip_counter = defaultdict(int)  # 记录IP出现次数

    try:
        with open(LOG_FILE_PATH, 'r') as file:
            lines = file.readlines()
            for line in lines:
                match = pattern.match(line)
                if match:
                    log_time = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S.%f')
                    if log_time >= time_threshold:
                        logger.debug(f"Log entry at {log_time} is within the time threshold")
                        connection_name = match.group(2)
                        ip = match.group(3)
                        if connection_name in TARGET_NAMES and not check_ip_whitelisted(ip):
                            ip_counter[ip] += 1  # 计数IP出现次数

        # 检查IP出现次数是否达到阈值
        for ip, count in ip_counter.items():
            if count >= THRESHOLD_COUNT:
                update_ban_list(ip)

    except FileNotFoundError as e:
        logger.error(f"Log file not found: {e}")
    except Exception as e:
        logger.error(f"Error reading log file: {e}")


def main_loop():
    while True:
        analyze_log()
        next_check = datetime.now() + timedelta(minutes=CHECK_INTERVAL)
        logger.info(f"Next check scheduled at {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
        sleep(CHECK_INTERVAL * 60)


if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
