#!/bin/bash

# This script is meant to be run by cron to trigger the Builder-Trainer loop
# Example crontab entry:
# */30 * * * * /path/to/builder_trainer_ai/cron.sh >> /path/to/builder_trainer_ai/memory/logs/cron.log 2>&1

# Change to the script directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if the loop is already running
if pgrep -f "python loop.py" > /dev/null; then
    echo "$(date): Loop is already running, skipping execution"
    exit 0
fi

# Start the loop
echo "$(date): Starting Builder-Trainer loop"
python loop.py

