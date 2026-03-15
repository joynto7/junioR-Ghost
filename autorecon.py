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

def run_scan(target:str, scan_key: str, output_dir: Path, save_output:bool) -> dict:
    info = SCANS[scan_key]   
    cmd = [c.replace("{target}",target) for c in info["cmd"]]

    log(f"Starting: {C.BOLD}{info['name']}{C.RESET} ({info['desc']}", "SECTION")
    log(f"Command: {C.DIM}{' '.join(cmd)}{C.RESET}")

    result = {
        "scan": scan_key,   
        "name": info["name"],
        "target": target,
        "command": " ".join(cmd),
        "timestamp": datetime.datetime.now().isoformat(),
        "output": "",
        "status": "ok"
    }
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        output = proc.stdout + proc.stderr
        result["output"] = output
        result["returncode"] = proc.returncode

        print(f"\n{C.DIM}{'─'*70}{C.RESET}")
        print(output.strip())
        print(f"{C.DIM}{'─'*70}{C.RESET}\n")

        if save_output:
            out_file = output_dir / f"{target.replace('.','_')}_{info['output_suffix']}.txt"
            out_file.write_text(
                f"Scan: {info['name']}\nTarget:{target}\nTime: {result['timestamp']}\n"
                f"Command: {result['command']}\n\n{'='*60}\n\n{output}"
            )
            log(f"Saved -> {out_file}","OK")
    except subprocess.TimeoutExpired:
        log(f"Scan '{scan_key}' timed out after 5 minutes.", " WARN")
        result["status"] = "timeout"
    except PermissionError:
        log(f"Scan '{scan_key}' requires root/sudo privileges.", "ERR")
        result["status"] = "permission_denied"    
    except Exception as e:
        log(f"Scan '{scan_key}' failed: {e}", "ERR")
        result["status"] = "error"
        result["error"] = str(e)

    return result 

def print_summery( results:list, output_dir: Path,save:bool)
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")
    print(f"{C.BOLD} RECON SUMMARY{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")

    ok = [ r for r in results if r ["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]

    for r in results:
        icon = f"{C.GREEN}✓{C.RESET}" if r["status"] == "ok" else f"{C.RED}✗{C.RESET}"
        status_color = C.GREEN if r["status"] == "ok" else C.RED
        print(f"  {icon} {r['name']:<35} {status_color}{r['status']}{C.RESET}")

    print(f"\n  Total: {len(results)} | {C.GREEN}OK: {len(ok)}{C.RESET} | {C.RED}Failed: {len(failed)}{C.RESET}")

    if save:
        summary_path = output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)
        log(f"Full summary saved → {summary_path}", "OK")

    print(f"\n  Total: {len(results)} | {C.GREEN}OK: {len(ok)}{C.RESET} | {C.RED}Failed: {len(failed)}{C.RESET}")

    if save:
        summary_path = output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)
        log(f"Full summary saved → {summary_path}", "OK")

    print(f"{C.BOLD}{C.BLUE}{'═'*60}{C.RESET}\n")


    
        

       