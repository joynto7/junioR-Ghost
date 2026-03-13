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