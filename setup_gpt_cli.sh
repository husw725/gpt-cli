#!/bin/bash

# Get the absolute path to the gpt-cli directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$INSTALL_DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python"
WRAPPER_SCRIPT="/usr/local/bin/gpt-cli"

echo "Setting up gpt-cli wrapper..."

# Create a wrapper script in /usr/local/bin
sudo tee "$WRAPPER_SCRIPT" > /dev/null <<EOL
#!/bin/bash
# Run gpt-cli from its home directory using its virtual environment
cd "$INSTALL_DIR"
"$PYTHON_BIN" "$INSTALL_DIR/main.py" "\$@"
EOL

# Make the wrapper executable
sudo chmod +x "$WRAPPER_SCRIPT"

echo "Success! You can now use 'gpt-cli' from any folder."
echo "Try running: gpt-cli chat 'hello'"
