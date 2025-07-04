#!/bin/bash
# WSL-specific installer for Python Alias Manager
# This script helps set up the alias manager properly in WSL environments
# 
# Features:
# - Automatically finds python_alias_manager.py in the same directory
# - Checks for Python availability in WSL
# - Sets up PATH configuration
# - Tests the installation
# 
# Usage: bash install_wsl.sh

echo "Python Alias Manager - WSL Installer"
echo "===================================="

# Check if we're in WSL
if ! (command -v wslpath &> /dev/null || [[ "$PWD" == /mnt/* ]]); then
    echo "This installer is specifically for WSL environments."
    echo "Use the regular Python installer instead: python install_alias_manager.py"
    exit 1
fi

# Check if Python is available in WSL
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python not found in WSL."
    echo "Please install Python first:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip"
    echo ""
    echo "Then run this installer again."
    exit 1
fi

echo "✓ WSL environment detected"
echo "✓ Python available"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for required Python scripts in the same directory as this installer
ALIAS_MANAGER="$SCRIPT_DIR/python_alias_manager.py"
if [[ ! -f "$ALIAS_MANAGER" ]]; then
    echo "Error: python_alias_manager.py not found at $ALIAS_MANAGER"
    echo ""
    echo "Make sure python_alias_manager.py is in the same directory as this installer."
    echo "Current script directory: $SCRIPT_DIR"
    echo ""
    echo "Available files in current directory:"
    ls -la "$SCRIPT_DIR"/*.py 2>/dev/null || echo "  No Python files found"
    exit 1
fi

echo "Found alias manager script: $ALIAS_MANAGER"

# Create WSL-specific installation directory
WSL_INSTALL_DIR="$HOME/.python_aliases/manager"
mkdir -p "$WSL_INSTALL_DIR"

# Copy the alias manager script to WSL filesystem for better performance
cp "$ALIAS_MANAGER" "$WSL_INSTALL_DIR/"
echo "✓ Copied alias manager to WSL filesystem: $WSL_INSTALL_DIR/python_alias_manager.py"

# Create WSL-optimized shell script for pam
cat > "$WSL_INSTALL_DIR/pam" << 'EOF'
#!/bin/bash
# WSL-optimized Python Alias Manager launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER_SCRIPT="$SCRIPT_DIR/python_alias_manager.py"

# Use WSL Python
if command -v python3 &> /dev/null; then
    python3 "$MANAGER_SCRIPT" "$@"
elif command -v python &> /dev/null; then
    python "$MANAGER_SCRIPT" "$@"
else
    echo "Error: Python not found. Please install Python in WSL:"
    echo "  sudo apt update && sudo apt install python3"
    exit 1
fi
EOF

chmod +x "$WSL_INSTALL_DIR/pam"
echo "✓ Created WSL-optimized pam script: $WSL_INSTALL_DIR/pam"

# Check if directory is in PATH
if ! echo "$PATH" | grep -q "$WSL_INSTALL_DIR"; then
    echo ""
    echo "⚠️  PATH Setup Required:"
    echo "Add this line to your ~/.bashrc:"
    echo "  export PATH=\"\$PATH:$WSL_INSTALL_DIR\""
    echo ""
    echo "Then run: source ~/.bashrc"
    echo ""
    
    read -p "Would you like me to add it to ~/.bashrc automatically? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! grep -q "python_aliases/manager" ~/.bashrc 2>/dev/null; then
            echo "# Python Alias Manager - added by install_wsl.sh" >> ~/.bashrc
            echo "export PATH=\"\$PATH:$WSL_INSTALL_DIR\"" >> ~/.bashrc
            echo "✓ Added to ~/.bashrc"
            echo "Please run: source ~/.bashrc (or restart your WSL session)"
        else
            echo "✓ PATH already configured in ~/.bashrc"
        fi
    else
        echo "Manual setup required. Add the export line to your ~/.bashrc"
    fi
else
    echo "✓ Directory already in PATH"
fi

echo ""
echo "Installation complete!"
echo ""

# Test the installation
echo "Testing installation..."
if "$WSL_INSTALL_DIR/pam" --help &> /dev/null; then
    echo "✓ Installation test passed!"
    
    # Check for existing aliases that might need fixing
    ALIAS_BIN_DIR="$HOME/.python_aliases/bin"
    if [[ -d "$ALIAS_BIN_DIR" ]]; then
        BROKEN_ALIASES=$(grep -l "python \"\$SCRIPT_PATH\"" "$ALIAS_BIN_DIR"/* 2>/dev/null | wc -l)
        if [[ $BROKEN_ALIASES -gt 0 ]]; then
            echo ""
            echo "⚠️  Found $BROKEN_ALIASES existing aliases that may have Python compatibility issues."
            echo "   These aliases were created before the WSL improvements."
            echo ""
            read -p "Would you like to recreate them with WSL-compatible Python detection? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "Listing current aliases to recreate:"
                "$WSL_INSTALL_DIR/pam" list
                echo ""
                echo "To fix existing aliases, you can update them:"
                echo "  pam update alias_name /path/to/script.py"
                echo ""
                echo "Or remove and re-add them:"
                echo "  pam remove alias_name"
                echo "  pam add alias_name /path/to/script.py"
            fi
        fi
    fi
else
    echo "⚠️  Installation test failed. You may need to:"
    echo "   1. Run: source ~/.bashrc"
    echo "   2. Restart your WSL session"
    echo "   3. Check Python installation"
fi

echo ""
echo "Usage in WSL:"
echo "  pam add myapp /mnt/c/path/to/script.py    # For Windows scripts"
echo "  pam add myapp ~/my_script.py              # For WSL scripts"
echo "  pam list"
echo "  pam setup"
echo "  pam venv alias_name                       # Check virtual environment info"
echo ""
echo "Features:"
echo "• Automatic virtual environment detection"
echo "• Cross-platform path conversion (Windows ↔ WSL)"
echo "• Works with venv, conda, and project dependencies"
echo ""
echo "Note: This setup works specifically in WSL and handles path conversion"
echo "between Windows and WSL filesystems automatically."
