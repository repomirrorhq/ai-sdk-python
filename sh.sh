#!/bin/bash

# Setup script for assistant-ui development environment
# This script installs nvm, Node LTS, Bun, say, Claude Code, and clones repositories

set -e

echo "========================================="
echo "Assistant UI Development Environment Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Update package list
print_info "Updating package list..."
sudo apt-get update

# Install prerequisites
print_info "Installing prerequisites..."
sudo apt-get install -y curl wget git build-essential unzip zip

# Install NVM (Node Version Manager)
print_info "Installing NVM..."
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Load NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    
    print_status "NVM installed successfully"
else
    print_info "NVM already installed, skipping..."
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Install Node.js LTS
print_info "Installing Node.js LTS..."
nvm install --lts
nvm use --lts
nvm alias default lts/*
print_status "Node.js LTS installed: $(node --version)"

# Install Bun
print_info "Installing Bun..."
if ! command -v bun &> /dev/null; then
    curl -fsSL https://bun.sh/install | bash
    
    # Add Bun to PATH for current session
    export BUN_INSTALL="$HOME/.bun"
    export PATH=$BUN_INSTALL/bin:$PATH
    
    print_status "Bun installed: $(bun --version)"
else
    print_info "Bun already installed: $(bun --version)"
fi

# Install say command (text-to-speech)
print_info "Installing say command..."
if ! command -v say &> /dev/null; then
    sudo apt-get install -y gnustep-gui-runtime
    print_status "Say command installed"
else
    print_info "Say command already installed"
fi

# Install Claude Code CLI
print_info "Installing Claude Code CLI..."
if ! command -v claude &> /dev/null; then
    # Check if npm is available
    if command -v npm &> /dev/null; then
        npm install -g @anthropic-ai/claude-code
        print_status "Claude Code CLI installed"
    else
        print_error "npm not found, please install Node.js first"
    fi
else
    print_info "Claude Code CLI already installed"
fi

# Create development directory if it doesn't exist
DEV_DIR="$HOME/development"
if [ ! -d "$DEV_DIR" ]; then
    print_info "Creating development directory at $DEV_DIR..."
    mkdir -p "$DEV_DIR"
fi

cd "$DEV_DIR"

# Clone assistant-ui-react repository
print_info "Cloning assistant-ui/assistant-ui repository..."
if [ ! -d "assistant-ui" ]; then
    git clone https://github.com/assistant-ui/assistant-ui.git
    print_status "assistant-ui repository cloned"
else
    print_info "assistant-ui repository already exists, pulling latest changes..."
    cd assistant-ui
    git pull
    cd ..
fi

# Clone Yonom/assistant-ui-vue repository
print_info "Cloning Yonom/assistant-ui-vue repository..."
if [ ! -d "assistant-ui-vue" ]; then
    git clone https://github.com/Yonom/assistant-ui-vue.git
    print_status "assistant-ui-vue repository cloned"
else
    print_info "assistant-ui-vue repository already exists, pulling latest changes..."
    cd assistant-ui-vue
    git pull
    cd ..
fi

# Update shell configuration
print_info "Updating shell configuration..."

# Function to add to shell config if not already present
add_to_shell_config() {
    local file=$1
    local line=$2
    if [ -f "$file" ]; then
        if ! grep -Fxq "$line" "$file"; then
            echo "$line" >> "$file"
        fi
    fi
}

# Determine shell config file
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

# Add NVM to shell config
add_to_shell_config "$SHELL_CONFIG" 'export NVM_DIR="$HOME/.nvm"'
add_to_shell_config "$SHELL_CONFIG" '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"'
add_to_shell_config "$SHELL_CONFIG" '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"'

# Add Bun to shell config
add_to_shell_config "$SHELL_CONFIG" 'export BUN_INSTALL="$HOME/.bun"'
add_to_shell_config "$SHELL_CONFIG" 'export PATH=$BUN_INSTALL/bin:$PATH'

echo ""
echo "========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Installed components:"
echo "  ✓ NVM (Node Version Manager)"
echo "  ✓ Node.js LTS: $(node --version 2>/dev/null || echo 'Please restart shell')"
echo "  ✓ npm: $(npm --version 2>/dev/null || echo 'Please restart shell')"
echo "  ✓ Bun: $(bun --version 2>/dev/null || echo 'Please restart shell')"
echo "  ✓ say command (text-to-speech)"
echo "  ✓ Claude Code CLI"
echo ""
echo "Cloned repositories to $DEV_DIR:"
echo "  ✓ assistant-ui"
echo "  ✓ assistant-ui-vue"
echo ""
echo -e "${YELLOW}Please restart your shell or run:${NC}"
echo "  source $SHELL_CONFIG"
echo ""
echo "To verify the installation, run:"
echo "  node --version"
echo "  bun --version"
echo "  claude --version"
