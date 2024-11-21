#/bin/bash
#### -------------------------   STOP MLOPS SERVERS  ----------------------------
dir=$(pwd)
cd ../MLOPs-template/
bash bash/stop-servers.sh
docker system prune -f