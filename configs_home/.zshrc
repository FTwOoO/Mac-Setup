#!/usr/bin/env zsh

CURRENT_FILE=`readlink ~/.zshrc`

if [ "$CURRENT_FILE" = "" ]
then
    CURRENT_DIR=`dirname $0`
else
    CURRENT_DIR=`dirname $CURRENT_FILE`
fi

source $CURRENT_DIR/zsh/aliases.sh
source $CURRENT_DIR/zsh/exports.sh
source $CURRENT_DIR/zsh/functions.sh
source $CURRENT_DIR/zsh/path.sh

source $CURRENT_DIR/zsh/programs/oh_my_zsh.sh
source $CURRENT_DIR/zsh/programs/programs.sh
