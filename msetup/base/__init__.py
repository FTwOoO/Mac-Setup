#!/usr/bin/env python3
import os.path
import sys

from pathlib import Path

HOME_DIR = ""
DEFAULT_CONFIGS_DIR =""
DEFAULT_BIN_DIR = ""
PACKAGES_INFO_FILE = ""

def setup_base_dir(base_dri:str):
    sys.path.append(base_dri)
    global HOME_DIR, DEFAULT_CONFIGS_DIR,DEFAULT_BIN_DIR,PACKAGES_INFO_FILE
    HOME_DIR = os.path.abspath(os.path.expanduser("~"))
    DEFAULT_CONFIGS_DIR = os.path.join(base_dri, "configs_home/")
    DEFAULT_BIN_DIR = os.path.join(base_dri, "bin/")


    PACKAGES_INFO_FILE = os.path.join(base_dri, "install.json")




