#!/bin/bash

# # Install required Python packages
# pip install kafka-python-ng structlog rich pendulum
# pip install /external-addons/data_transforms_py-0.1.0-cp311-cp311-linux_x86_64.whl --force-reinstall

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the name of the current script
SCRIPT_NAME="$(basename -- "$0")"

# Get all .py files in the current directory except the script itself
addon_files=()
for file in "$SCRIPT_DIR"/*.py; do
    if [[ "$(basename -- "$file")" != "$SCRIPT_NAME" ]]; then
        addon_files+=("$file")
    fi
done

# Construct the mitmdump command with all addons
mitmdump_command="mitmdump --showhost"
for addon_file in "${addon_files[@]}"; do
    mitmdump_command+=" -s $addon_file"
done

echo "Running mitmdump with the following addons:"
echo "$mitmdump_command"

# Execute the mitmdump command
eval "$mitmdump_command"
