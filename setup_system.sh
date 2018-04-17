#!/usr/bin/env bash

sudo softwareupdate -ia --verbose
xcode-select --install

### zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
source ~/.zshrc

### golang
./install_app.py go

### python
./install_app.py python
pip3 install ansible
