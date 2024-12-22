#!/bin/bash

# open MLOps frameworks
#### -------------------------   RUN MLOPS SERVERS  ----------------------------
dir=$(pwd)
project_name="${PWD##*/}"

# run the mlops servers
mlops_dir=../MLOPs-template/
cd $mlops_dir
bash bash/open-servers-browser.sh

# create an alias to the jenkins outputs
ln -s "$(pwd)/jenkins-data/jobs" ../../jenkins-outputs

#### ---------------   LOAD / SHOW THE SERVERS IPS SERVERS  --------------------
cp .env-ip $dir/.env-ip-mlops
cp .env $dir/.env-mlops

cd $dir
. .env-ip-mlops
. .env
#### -----------------------   UPDATE MLFLOW  URI -------------------------------
echo && echo "[${PROJECT_NAME}][Docker-Compose] Updating the configuration file..."

if [ "$MLFLOW_SERVER_URL" != "" ] ; then
	#### --------------------   UPDATE THE MLFLOW_URI  -------------------------
	echo "   -> updating the mlflow_uri in <config/config.yaml> file "
	sed -i "s|mlflow_uri:.*|mlflow_uri: $MLFLOW_SERVER_URL|g" config/config.yaml
	echo "   -> S3_LOCAL_DIR=${S3_LOCAL_DIR}"
	# xdg-open "${MLFLOW_SERVER_URL}"
fi

# run the projects servers
echo $(pwd)
bash bash/4-open-app-servres-in-browser.sh
