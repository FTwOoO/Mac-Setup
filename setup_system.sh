#!/usr/bin/env bash

sudo softwareupdate -ia --verbose
xcode-select --install

### zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
./setup_system.py zsh
source ~/.zshrc

#./osx.sh

### golang
./install_app.py go

### python
./install_app.py python
pip3 install ansible
