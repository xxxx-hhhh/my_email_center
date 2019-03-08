#!/usr/bin/env bash
# 本地环境


cd `dirname "$0" | xargs dirname`

PATH_DEPLOY=./_deploy

if [ -d "${PATH_DEPLOY}" ]; then
    rm -rf ${PATH_DEPLOY}
fi

mkdir ${PATH_DEPLOY}

git archive HEAD --prefix='email_center/' | gzip > ${PATH_DEPLOY}/email_center.tar.gz

cd ${PATH_DEPLOY}


###########################

cp email_center.tar.gz ~/

cd ~/
tar xzvfp email_center.tar.gz

cd ~/email_center
pip install -r ./requirements.txt
echo "requirements updated"

export EMAIL_CENTER_CONFIG_TYPE="development"
echo "set environment parament"

./update-database.sh
echo "db updated"

supervisorctl -c supervisord.conf update
echo "supervisor config updated"

supervisorctl -c supervisord.conf restart all
echo "all restart"

#################################

cd ..
rm -rf ${PATH_DEPLOY}