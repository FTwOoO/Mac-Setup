#!/bin/sh

CURRENT_FILE=`readlink ~/.zshrc`
CURRENT_DIR=`dirname $CURRENT_FILE`

source $CURRENT_DIR/aliases.sh
source $CURRENT_DIR/exports.sh
source $CURRENT_DIR/functions.sh
source $CURRENT_DIR/path.sh

source $CURRENT_DIR/programs/oh_my_zsh.sh
source $CURRENT_DIR/programs/programs.sh
