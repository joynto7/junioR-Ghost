#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║              AutoRecon - Universal Nmap Recon Tool        ║
║              Author  : Ghost (Joynto Ghosh)               ║
║              Purpose : Multi-mode recon on a single IP    ║
╚═══════════════════════════════════════════════════════════╝
"""

import argparse
import subprocess
import sys
import os
import json
import datetime
from pathlib import Path
class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"
    BANNER = f"""
{C.CYAN}{C.BOLD}
  ░█████╗░██╗░░░██╗████████╗░█████╗░██████╗░███████╗░█████╗░░█████╗░███╗░░██╗
  ██╔══██╗██║░░░██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗░██║
  ███████║██║░░░██║░░░██║░░░██║░░██║██████╔╝█████╗░░██║░░╚═╝██║░░██║██╔██╗██║
  ██╔══██║██║░░░██║░░░██║░░░██║░░██║██╔══██╗██╔══╝░░██║░░██╗██║░░██║██║╚████║
  ██║░░██║╚██████╔╝░░░██║░░░╚█████╔╝██║░░██║███████╗╚█████╔╝╚█████╔╝██║░╚███║
  ╚═╝░░╚═╝░╚═════╝░░░╚═╝░░░░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░░╚════╝░╚═╝░░╚══╝
{C.RESET}{C.DIM}  Universal Nmap Recon Script | by Ghost{C.RESET}
"""
SCANS = {

    "port": {
            "name": "Full Port Scan",
            "desc": "Scans all 65535 TCP prots",
            "cmd": ["nmap", "-p-", "--open", "-T4", "--min-rate=1000", "{target}"],
            "output_suffix": "ports"
        },
    "service": {
        "name": "Service and Version Detection",
        "desc": "Finding  the services and versions of common ports",
        "cmd": ["nmap","-sV","-sC","-p","21,22,23,25,53,80,110,143,443,445,3306,3389,8080,8443","{target}"],
        "output_suffix": "services"
    },

    "os":{
        "name": " OS Detection",
        "desc": " Identify which os runing ",
        "cmd": ["nmap", "-O", "--osscan-guess", "{target}"],
        "output_suffix": "os"
    },

    "vuln": {
        "name": "Vulnerability Scan",
        "desc": "Runs NSE vulnerability scripts (CVEs, common misconfigs)",
        "cmd": ["nmap", "--script", "vuln", "-T4", "{target}"],
        "output_suffix": "vulns"
    },
       "banner": {
        "name": "Banner Grabbing",
        "desc": "Grabs banners from open ports",
        "cmd": ["nmap", "--script", "banner", "-p-", "--open", "{target}"],
        "output_suffix": "banners"
    },
        "udp": {
        "name": "Top 100 UDP Scan",
        "desc": "Scans top 100 UDP ports (requires root/sudo)",
        "cmd": ["nmap", "-sU", "--top-ports", "100", "-T4", "{target}"],
        "output_suffix": "udp"
    },
    "http": {
        "name": "HTTP Enumeration",
        "desc": "Enumerates HTTP/HTTPS services (titles, headers, methods)",
        "cmd": ["nmap", "--script", "http-title,http-headers,http-methods,http-robots.txt,http-auth-finder",
                "-p", "80,443,8080,8443,8888", "{target}"],
        "output_suffix": "http"
    },
     "smb": {
        "name": "SMB Enumeration",
        "desc": "Enumerates SMB shares, signing, OS info (Windows targets)",
        "cmd": ["nmap", "--script", "smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode",
                "-p", "139,445", "{target}"],
        "output_suffix": "smb"
    },
    "ftp": {
        "name": "FTP Enumeration",
        "desc": "Checks FTP anonymous login and version",
        "cmd": ["nmap", "--script", "ftp-anon,ftp-bounce,ftp-syst", "-p", "21", "{target}"],
        "output_suffix": "ftp"
    },
    "dns": {
        "name": "DNS Enumeration",
        "desc": "Enumerates DNS records and zone transfers",
        "cmd": ["nmap", "--script", "dns-zone-transfer,dns-brute,dns-recursion", "-p", "53", "{target}"],
        "output_suffix": "dns"
    },
    "ssh": {
        "name": "SSH Audit",
        "desc": "Checks SSH version and supported auth methods",
        "cmd": ["nmap", "--script", "ssh-auth-methods,ssh2-enum-algos", "-p", "22", "{target}"],
        "output_suffix": "ssh"
    },
    "quick": {
        "name": "Quick Scan (Default)",
        "desc": "Fast scan of top 1000 ports with service detection",
        "cmd": ["nmap", "-sV", "-T4", "--open", "{target}"],
        "output_suffix": "quick"
    },
    "aggressive": {
        "name": "Aggressive Scan",
        "desc": "Full aggressive scan: OS, version, scripts, traceroute",
        "cmd": ["nmap", "-A", "-T4", "--open", "{target}"],
        "output_suffix": "aggressive"
    },
    "stealth": {
        "name": "Stealth SYN Scan",
        "desc": "Low-noise SYN scan (requires root/sudo)",
        "cmd": ["nmap", "-sS", "-T2", "--open", "-p-", "{target}"],
        "output_suffix": "stealth"
    },
    "firewall": {
        "name": "Firewall / IDS Evasion Test",
        "desc": "Tests basic firewall evasion techniques",
        "cmd": ["nmap", "-f", "--mtu", "24", "-D", "RND:5", "--data-length", "200", "{target}"],
        "output_suffix": "firewall"
    },
}

ALL_SCAN_KEYS = list(SCANS.keys())

def log(msg, level ="INFO"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO":  f"{C.CYAN}[*]{C.RESET}",
        "OK":    f"{C.GREEN}[+]{C.RESET}",
        "WARN":  f"{C.YELLOW}[!]{C.RESET}",
        "ERR":   f"{C.RED}[-]{C.RESET}",
        "SECTION":f"{C.BLUE}[>]{C.RESET}",
    }.get(level,"[?]")
    print(f"{C.DIM}{ts}{C.RESET}{prefix}{msg}")
    
def check_map():
    try:
        subprocess.run["namp","--version"], capture_output=True, check=True)
        return True 
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    
def is_root():
    return os.geteuid() == 0

def print_scan_menu():
    print(f"\n{C.BOLD}Acvailable Scan Modules:{C.RESET}")
    print(f" {'KEY':<12} {'NAME':<30} DESCRIPTION")
    print(f"  {'-'*12} {'-'*30} {'-'*40}")
    for key, info in SCANS.items():
        print(f"  {C.CYAN}{key:<12}{C.RESET} {info['name']:<30} {C.DIM}{info['desc']}{C.RESET}")
    print()    

       