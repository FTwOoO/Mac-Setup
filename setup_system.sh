#!/usr/bin/env bash

sudo softwareupdate -ia --verbose
xcode-select --install

### zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
./setup_system.py zsh
source ~/.zshrc

#./osx.sh

### golang
./setup_system.py go

# delve debugger
go get -u github.com/derekparker/delve

# gox
go get github.com/mitchellh/gox
cd $GOPATH/src/github.com/mitchellh/gox/main
go generate

### python
./setup_system.py python
pip3 install ansible
