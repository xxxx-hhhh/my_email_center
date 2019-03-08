#!/usr/bin/env bash
# 线上环境


cd `dirname "$0" | xargs dirname`

PATH_DEPLOY=./_deploy

if [ -d "${PATH_DEPLOY}" ]; then
    rm -rf ${PATH_DEPLOY}
fi

mkdir ${PATH_DEPLOY}

git archive HEAD --prefix='email_center/' | gzip > ${PATH_DEPLOY}/email_center.tar.gz

cd ${PATH_DEPLOY}

# qddata##1
scp -P PORT email_center.tar.gz qddata@39.108.11.128:~/email_center

###########################
# USER##1
# scp -P PORT email_center.tar.gz USER@IP:/opt
# ssh -p PORT USER@IP 'cd /opt/; tar xzvfp email_center.tar.gz '

# ssh -p PORT USER@IP  'cd /opt/email_center; pip install -r ./requirements.txt'
# echo 'requirements updated'

# ssh -p PORT USER@IP  'cd /opt/email_center; source ./set-env.sh'
# echo 'set environment parament'

# ssh -p PORT USER@IP 'cd /opt/email_center; ./update-database.sh'
# echo 'db updated'

# ssh -p PORT USER@IP  'cd /opt/email_center; supervisorctl -c supervisord.conf update'
# echo 'supervisor config updated'

# ssh -p PORT USER@IP  'cd /opt/email_center; supervisorctl -c supervisord.conf restart all'
# echo 'all restart'

#################################

cd ..
rm -rf ${PATH_DEPLOY}
