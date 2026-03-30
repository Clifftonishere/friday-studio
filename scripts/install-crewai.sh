#!/bin/bash
set -e
echo "Installing CrewAI inside friday-animateme..."
docker exec -it --user root friday-animateme bash -c "apt-get update -qq && apt-get install -y python3 python3-pip python3-venv -qq && python3 -m venv /home/node/crewai-env && /home/node/crewai-env/bin/pip install crewai openai anthropic requests --quiet && echo 'CrewAI installed.'"
