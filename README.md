
# FRPS 日志 IP 封禁工具

此工具旨在增强 FRP (Fast Reverse Proxy) 的安全性，通过监控 FRPS 日志文件，自动封禁频繁尝试连接的异常 IP 地址。

## 功能特性
- 在frp 0.52-0.60测试通过，只要frp不改动当前（0.60版本）的日志格式都能适用
- 自动监控 FRPS 日志文件。
- 根据配置的时间阈值和尝试次数自动封禁异常 IP。
- 支持设置白名单 IP。
- 封禁的 IP 地址会记录并在设定时间后自动解封。
- 支持 Windows 和 Linux 系统（宝塔面板所用的ufw管理防火墙）。
- 仅支持ipv4

## 快速开始

1. 克隆仓库或下载项目文件。
   ```
   git clone https://github.com/zsanjin-p/frps-log-ip-ban
   ```

2. 修改 `.env` 环境变量文件，根据您的环境配置以下变量：

   - `LOG_FILE_PATH`: FRPS 日志文件路径。
   - `TARGET_NAMES`: 目标连接名称标记内容，逗号分隔。
   - `WHITELIST`: IP 白名单，逗号分隔。
   - `BAN_FILE_PATH`: 被禁 IP 的文件路径。
   - `EXECUTE_PATH`: 检测到被禁 IP 时要执行的脚本或程序路径。
   - `CHECK_INTERVAL`: 检查日志文件的时间间隔（分钟）。
   - `THRESHOLD_COUNT`: 触发禁用 IP 的次数阈值。

3. 根据您的操作系统选择对应的封禁 IP 脚本：

   - Windows: `banip.ps1`
   - Linux (宝塔面板UFW): `banip.py`

## 配置和使用

### Windows

1. 修改 `banip.ps1` 脚本，设置黑名单文件路径和封禁天数（默认为当天往前数30天）。
黑名单文件所在的位置：必改，大概在第10行左右，banip.ps1脚本默认为C:\\Users\\Administrator\\Desktop\\banip\\frplog\\banip.txt
封禁天数：把banip.ps1大概第6行$thresholdDate = (Get-Date).AddDays(-30)改为$thresholdDate = (Get-Date).AddDays(-99999)或者$thresholdDate = (Get-Date).AddDays(-30)改为$thresholdDate = (Get-Date).AddDays(99999)

2. 点击运行frpbanip.py即可。

3. 创建批处理文件 `.bat` 并通过计划任务程序可设置开机启动：
   ```bat
   @echo off
   cd C:\Users\Administrator\Desktop\banip\frplog
   C:\Path\To\Python\python.exe frpbanip.py
   ```

### Linux

1. 修改 `banip.py` 脚本，适用于使用宝塔面板（UFW）管理防火墙的系统，设置黑名单文件路径和封禁天数（默认为当天往前数30天）。
黑名单文件所在的位置：必改，大概在第9行左右，banip.py脚本默认为/root/firewall/banipufw/banip.txt
封禁天数：把banip.py大概第6行threshold_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')改为threshold_date = (datetime.datetime.now() - datetime.timedelta(days=99999)).strftime('%Y-%m-%d')

2. 输入命令 `pyhton frpbanip.py` 即可运行。

3. 创建 Systemd 服务文件 `/etc/systemd/system/frpbanip.service`，将下面内容添加进去，注意修改 Python 路径和工作目录路径。

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


   重新加载 Systemd 配置并启动服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start frpbanip
   sudo systemctl enable frpbanip
   ```


*注意目前有一种难以防范的情况：比如设置了5分钟检查一次日志，你的远程桌面设置为10分钟内密码错误5次则锁定10分钟，然而在某个5分钟内连续有大量的ip在爆破，而本检测封禁脚本并未到检测时间，这时候你使用远程桌面时会发现被锁，不过根据你远程桌面的设置，10分钟后即可使用，同时那些爆破的ip也被封禁了。这种情况比较少见，除非你泄露了ip被轮了，可以通过缩短检测封禁时间和缩短远程桌面锁定时间来解决问题。


## 许可证

本项目采用 BSD 2-Clause 或 3-Clause 许可证。

BSD 3-Clause License

Copyright (c) 2024, zsanjin
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the zsanjin nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## 贡献

如果您喜欢此项目，请考虑给我们一个星标（star）！


