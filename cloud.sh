#!/bin/bash
# (It's good practice to have this shebang at the top)

cat <<'EOF'
 _      ____  ____  _     
/ \__/|/  _ \/  _ \/ \  /|
| |\/||| / \|| / \|| |\ ||
| |  ||| \_/|| \_/|| | \||
\_/  \|\____/\____/\_/  \|
                          
Copyright (C) 2020-2023 by MoonTg-project@Github, < https://github.com/The-MoonTg-project >.
This file is part of < https://github.com/The-MoonTg-project/Moon-Userbot > project,
and is released under the "GNU v3.0 License Agreement".
Please see < https://github.com/The-MoonTg-project/Moon-Userbot/blob/main/LICENSE >
All rights reserved.
EOF

# --- [MODIFIED LINE] ---
# This line now starts three processes in the correct order:
# 1. Gunicorn (web server) in the background.
# 2. The assistant bot in the background.
# 3. The main userbot in the foreground (which keeps the service alive).

gunicorn app:app --daemon && python3 -m assistant & && python3 main.py
