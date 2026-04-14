#!/bin/bash

# 1. Install Gemini CLI globally via npm
npm install -g @google/gemini-cli

# 2. Install GitHub Copilot CLI extension 
gh extension install github/gh-copilot --force

# 3. Create a Python Virtual Environment
python3 -m venv .venv

# 4. Activate and upgrade pip/install dependencies
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Setup complete! Use 'source .venv/bin/activate' to enter your Python environment."