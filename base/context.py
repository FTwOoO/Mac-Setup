#!/usr/bin/env python3

import contextlib
import json

import typing

import base
from base.config import Config
from base.install_info import InstallationInfo


class Context(contextlib.AbstractContextManager):
    config: Config
    installInfo: typing.Dict[str, InstallationInfo] = dict()

    def __init__(self, config: Config):
        self.config = config

    def __enter__(self):
        with open(base.PACKAGES_INFO_FILE, 'r') as f:
            try:
                d = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                return self

            for k, v in d.items():
                self.installInfo[k] = InstallationInfo(**v)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(base.PACKAGES_INFO_FILE, 'w') as f:
            d = {}
            for k, v in self.installInfo.items():
                d[k] = v._asdict()

            fileData = json.dumps(d)
            f.write(fileData)

