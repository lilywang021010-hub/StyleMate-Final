#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
if [ -x /opt/anaconda3/bin/pythonw ]; then
    exec /opt/anaconda3/bin/pythonw stylemate.py
else
    exec python3 stylemate.py
fi
