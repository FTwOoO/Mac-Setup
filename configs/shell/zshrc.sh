#!/usr/bin/env zsh

CURRENT_FILE=`readlink ${0}`
if [ "$CURRENT_FILE" = "" ]
then
     CURRENT_FILE="${0}"
fi

CURRENT_DIR=`dirname $CURRENT_FILE`

source $CURRENT_DIR/aliases.sh
source $CURRENT_DIR/exports.sh
source $CURRENT_DIR/functions.sh
source $CURRENT_DIR/path.sh

source $CURRENT_DIR/programs/oh_my_zsh.sh
source $CURRENT_DIR/programs/programs.sh
