#!/bin/bash

#######################################################
# ChatConvert Toolkit - Unix/Linux/macOS Launcher
# Automatically detects Python and runs the menu
#######################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "============================================================"
echo "   ChatConvert Toolkit - Unix/macOS/Linux Launcher"
echo "============================================================"
echo ""

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    local version=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)

    # Check if version is 3.6 or higher
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)

    if [ "$major" -ge 3 ] && [ "$minor" -ge 6 ]; then
        return 0
    else
        return 1
    fi
}

# Try python3 command
if command -v python3 &> /dev/null; then
    if check_python_version python3; then
        echo -e "${GREEN}✓ Python 3 found: python3${NC}"
        python3 --version
        echo ""
        echo "Starting ChatConvert Toolkit..."
        echo ""
        python3 menu.py
        exit 0
    fi
fi

# Try python command
if command -v python &> /dev/null; then
    # Check if it's Python 3
    if python --version 2>&1 | grep -q "Python 3"; then
        if check_python_version python; then
            echo -e "${GREEN}✓ Python 3 found: python${NC}"
            python --version
            echo ""
            echo "Starting ChatConvert Toolkit..."
            echo ""
            python menu.py
            exit 0
        fi
    fi
fi

# Python not found or version too old
echo -e "${RED}✗ Error: Python 3.6 or higher not found!${NC}"
echo ""
echo "Please install Python 3.6+ from:"
echo "  • macOS: brew install python3  OR  https://www.python.org/downloads/"
echo "  • Linux: sudo apt install python3  OR  sudo yum install python3"
echo ""
exit 1
