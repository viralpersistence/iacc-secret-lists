#!/usr/bin/env bash

set -e

if [ ! -d "flask_venv" ]; then
  virtualenv flask_venv || exit
fi

. flask_venv/bin/activate

pip install -r requirements.txt