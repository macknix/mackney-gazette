#!/bin/bash

# Script to initialize town and population data

echo "Initializing town and population data..."

# Activate virtual environment if it exists
if [ -f "mackney-gazette-venv/bin/activate" ]; then
    source mackney-gazette-venv/bin/activate
    echo "Activated virtual environment"
fi

# Run the initialization script
# Uses the town_init_config.yaml file in the project root by default
python -m src.initialise_town "$@"

# Exit with the same status as the Python script
exit $?
