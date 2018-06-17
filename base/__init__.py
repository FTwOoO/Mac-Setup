#!/usr/bin/env python3
import os.path
import sys

HOME_DIR = ""
DEFAULT_CONFIGS_DIR = ""
DEFAULT_BIN_DIR = ""
PACKAGES_INFO_FILE = ""


def setup_base_dir(base_dri: str):
    base_dri = os.path.abspath(base_dri)
    sys.path.append(base_dri)
    global HOME_DIR, DEFAULT_CONFIGS_DIR, DEFAULT_BIN_DIR, PACKAGES_INFO_FILE
    HOME_DIR = os.path.abspath(os.path.expanduser("~"))
    DEFAULT_CONFIGS_DIR = os.path.join(base_dri, "configs_home/")
    DEFAULT_BIN_DIR = os.path.abspath(base_dri)

    PACKAGES_INFO_FILE = os.path.join(base_dri, "install.json")

def get_bin_dir()->str:
    return DEFAULT_BIN_DIR

def get_config_dir()->str:
    return DEFAULT_CONFIGS_DIR