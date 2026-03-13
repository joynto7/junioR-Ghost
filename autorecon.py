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



}