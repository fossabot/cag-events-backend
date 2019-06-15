#!/bin/bash

DEV_SETTINGS_FILE="setup/venv/env.original"
SETTINGS_FILE="env"
LOG_DIR="log"
MANAGE="python src/manage.py"

set -e # Exit on error

# Activate venv and deactivate on exit
source manage/activate-venv.sh
trap deactivate EXIT

set -eu # Exit on error and undefined var is error

# Add settings file
if [[ ! -e $SETTINGS_FILE ]]; then
    echo "Adding sample settings file ..."
    mkdir -p $(dirname $SETTINGS_FILE)
    cp $DEV_SETTINGS_FILE $SETTINGS_FILE
fi

# Add other dirs and files
[[ ! -e $LOG_DIR ]] && mkdir -p $LOG_DIR

# Install requirements inside venv, and check for outdated packages
echo
echo "Installing requirements ..."
pip install --quiet -r requirements/development.txt

# Collect static files
echo
echo "Collecting static files ..."
# Ignore admin app, use theme instead
$MANAGE collectstatic -i admin --noinput --clear | egrep -v "^Deleting" || true

# Run migration, but skip initial if matching table names already exist
echo
echo "Running migration ..."
$MANAGE migrate --fake-initial

# Add superuser
#echo "Adding superuser ..."
#echo "Press CTRL+C to cancel"
#$MANAGE createsuperuser
