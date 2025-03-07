#!/bin/bash

# Move to the script's parent directory (assumes it's in src/production)
cd "$(dirname "$0")/../../"

# Define the virtual environment directory
VENV_DIR="venv"

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created in $VENV_DIR."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
if [[ "$SHELL" =~ "zsh" ]]; then
    source "$VENV_DIR/bin/activate"
else
    source "$VENV_DIR/bin/activate"
fi

# Install dependencies from requirements.txt if the file exists
if [ -f "src/production/requirements.txt" ]; then
    pip install -r src/production/requirements.txt
else◊
    echo "requirements.txt not found, skipping installation."
fi

# Run the pyside6-project command
pyside6-project build src