#!/usr/bin/env python3

import os.path

class ExportFile:
    @classmethod
    def add(cls, key: str, value: str):
        config_path = os.path.expanduser("~/.zsh")
        with open(config_path, "w") as f:
            f.write('export {}="{}"\n'.format(key, value))


class PathFile(ExportFile):
    @classmethod
    def export_path(cls, path):
        key = "PATH"
        value = '''$PATH:{path}'''.format(path=path)
        return cls.add(key, value)
