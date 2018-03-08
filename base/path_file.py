#!/usr/bin/env python3
import contextlib
import re


class ExportFile(contextlib.AbstractContextManager):
    def __init__(self, path):
        self.path = path

    def __parse_file(self, path: str) -> list:
        d = []
        for line in open(path, 'r'):
            m = re.match(r'^export \s+ (\w+) = "(.+)" \s*$', line, re.X)
            if m:
                d.append((m.group(1), m.group(2)))

        return d

    def __enter__(self):
        self.vars = self.__parse_file(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.path, "w") as f:
            for key, value in self.vars:
                f.write('export {}="{}"\n'.format(key, value))

    def add(self, key: str, value: str):
        self.vars.append((key, value))


class PathFile(ExportFile):
    def export_path(self, path):
        key = "PATH"
        value = '''$PATH:{path}'''.format(path=path)
        return self.add(key, value)

