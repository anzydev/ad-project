#!/bin/zsh
# Double-click to prepare the AD Project viva workspace on this Mac.
set -e
cd "$(dirname "$0")"

echo "Starting AD Project Data Engineering demo..."
./DE/scripts/setup_database.sh

if ! curl -fsS --max-time 3 http://127.0.0.1:8000/api/v1/health >/dev/null; then
  echo "Opening FastAPI backend terminal..."
  osascript -e 'tell application "Terminal" to do script "cd ~/Desktop/ad/ad-project && source .venv/bin/activate && uvicorn ad_project.api.app:app --host 127.0.0.1 --port 8000"'
  sleep 2
fi

echo "Opening live system monitor and PostgreSQL console..."
osascript <<'APPLESCRIPT'
tell application "Terminal"
  do script "cd ~/Desktop/ad/ad-project && source .venv/bin/activate && python main.py"
  do script "cd ~/Desktop/ad/ad-project && ./DE/scripts/viva_database_console.sh"
end tell
APPLESCRIPT

echo "Opening schema, ER diagram, Q1-Q5 guide, and verified results..."
"/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" --reuse-window \
  prisma/schema.prisma \
  DE/02_ER_DIAGRAM.md \
  DE/03_NORMALIZATION.md \
  DE/evidence/sql_queries_output.txt \
  DE/evidence/transactions_output.txt \
  DE/evidence/concurrency_output.txt \
  DE/evidence/performance_output.txt \
  DE/08_VIVA_DEMO.md \
  ad_project/api/routes.py

open -a "Brave Browser" "http://127.0.0.1:8000/docs"
open -a "OBS"

echo
echo "READY — PostgreSQL, FastAPI, live monitor, DB console, code and OBS."
echo "OBS is open but recording has NOT started."
