#!/bin/bash

# Script to generate daily articles

echo "Generating daily articles..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Run the article generation script
python3 -m src.generate_articles_daily "$@"

# Exit with the same status as the Python script
exit $?
