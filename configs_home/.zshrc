#!/usr/bin/env zsh

CURRENT_FILE=`readlink ~/.zshrc`

if [ "$CURRENT_FILE" = "" ]
then
    CURRENT_DIR=`dirname $0`
else
    CURRENT_DIR=`dirname $CURRENT_FILE`
fi

# MySQL Server Setting
export PATH="$PATH:/usr/local/mysql-5.7.18-macos10.12-x86_64/bin"

# Etcd setting
export ETCDCTL_API=3