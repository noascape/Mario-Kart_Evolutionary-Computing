#!/bin/bash

# 1. Install System Dependencies (Apt)
sudo apt-get update && sudo apt-get install -y \
    libzip-dev \
    libgl1 \
    libglib2.0-0 \
    libglu1-mesa \
    libglu1-mesa-dev \
    xvfb \
    python3-opengl \
    libsdl2-dev \
    freeglut3-dev \
    mesa-common-dev

# 2. Install Gemini CLI globally via npm
npm install -g @google/gemini-cli

# 3. Install GitHub Copilot CLI extension 
gh extension install github/gh-copilot --force

# 4. Create a Python Virtual Environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 5. Activate and upgrade pip/install dependencies
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 6. Setup custom retro integration
CUSTOM_INTEGRATION_PATH="$(pwd)/src/env/custom_integration/SuperMarioKart-Snes-v0"
RETRO_CONTRIB_PATH=".venv/lib/python3.11/site-packages/stable_retro/data/contrib/SuperMarioKart-Snes-v0"

if [ -d "$CUSTOM_INTEGRATION_PATH" ]; then
    echo "Registering custom SuperMarioKart integration..."
    mkdir -p "$(dirname "$RETRO_CONTRIB_PATH")"
    cp -r "$CUSTOM_INTEGRATION_PATH" "$RETRO_CONTRIB_PATH"
fi

# 7. Import ROM if present
if [ -f "rom/Super Mario Kart (USA).sfc" ]; then
    echo "ROM found, importing..."
    ./.venv/bin/python3 -m stable_retro.import rom/
fi

echo "Setup complete! Use 'source .venv/bin/activate' to enter your Python environment."
