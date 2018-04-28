#!/usr/bin/env python3
import os.path
import sys

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
HOME_DIR = os.path.abspath(os.path.expanduser("~"))
DEFAULT_CONFIGS_DIR = os.path.join(BASE_DIR, "configs_home/")
DEFAULT_BIN_DIR = os.path.join(BASE_DIR, "bin/")
PACKAGES_INFO_FILE = os.path.join(BASE_DIR, ".install.json")
