#!/usr/bin/env bash

sudo softwareupdate -ia --verbose
xcode-select --install

./osx.sh
./setup_system.py go python