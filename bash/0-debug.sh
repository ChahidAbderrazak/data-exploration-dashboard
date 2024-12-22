#!/bin/bash
# pip install flake8 black
#  debuggin the code
echo && echo "[${PROJECT_NAME}][dev] Linting the codes."
###----------------------------------------------------------------------
echo && echo  "Debuging the code..."
python -m flake8 . --count --select=E9,F63,F7,F82 --ignore=F541 --show-source --statistics
python -m flake8 . --count --ignore=F541,W503 --max-complexity=10 --max-line-length=127 --statistics
python -m black . ###check --diff

# echo && echo "Testing the code..."
# python -m pytest --verbose
