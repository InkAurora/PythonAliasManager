#!/bin/bash
# WSL-specific installer for Python Alias Manager
# This script helps set up the alias manager properly in WSL environments

echo "Python Alias Manager - WSL Installer"
echo "===================================="

# Check if we're in WSL
if ! (command -v wslpath &> /dev/null || [[ "$PWD" == /mnt/* ]]); then
    echo "This installer is specifically for WSL environments."
    echo "Use the regular Python installer instead."
    exit 1
fi

# Convert Windows paths to WSL paths
WINDOWS_DESKTOP="/mnt/c/Users/INK/Desktop"
if [[ ! -d "$WINDOWS_DESKTOP" ]]; then
    echo "Error: Windows Desktop directory not found at $WINDOWS_DESKTOP"
    echo "Please adjust the path in this script to match your setup."
    exit 1
fi

# Check for required Python scripts
ALIAS_MANAGER="$WINDOWS_DESKTOP/python_alias_manager.py"
if [[ ! -f "$ALIAS_MANAGER" ]]; then
    echo "Error: python_alias_manager.py not found at $ALIAS_MANAGER"
    exit 1
fi

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
            echo "export PATH=\"\$PATH:$WSL_INSTALL_DIR\"" >> ~/.bashrc
            echo "✓ Added to ~/.bashrc"
            echo "Please run: source ~/.bashrc"
        else
            echo "✓ PATH already configured in ~/.bashrc"
        fi
    fi
else
    echo "✓ Directory already in PATH"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage in WSL:"
echo "  pam add myapp /mnt/c/path/to/script.py    # For Windows scripts"
echo "  pam add myapp ~/my_script.py              # For WSL scripts"
echo "  pam list"
echo "  pam setup"
echo ""
echo "Note: This setup works specifically in WSL and handles path conversion"
echo "between Windows and WSL filesystems automatically."
