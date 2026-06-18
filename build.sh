#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
export FLASK_APP=run.py
flask db upgrade

# Seed database (Create Admin role and default user if not exists)
python seed.py
