#!/bin/bash
# Pebble Engine — Mac launcher
# Double-click this file to start the program.
# First time: right-click → Open (macOS may ask for permission on new apps).
#
# The terminal window that opens is the engine.
# Keep it in the background — closing it stops the program.

cd "$(dirname "$0")"

# If Python 3 is available, run the launcher
if command -v python3 &>/dev/null; then
    python3 launch.py
elif command -v python &>/dev/null; then
    python launch.py
else
    echo ""
    echo "  ✗ Python not found."
    echo ""
    echo "  Install Python from python.org and try again."
    echo ""
    read -p "  Press Enter to close."
fi
