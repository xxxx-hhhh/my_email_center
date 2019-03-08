#!/usr/bin/env bash
# 预发布环境


cd `dirname "$0" | xargs dirname`

PATH_DEPLOY=./_deploy

if [ -d "${PATH_DEPLOY}" ]; then
    rm -rf ${PATH_DEPLOY}
fi

mkdir ${PATH_DEPLOY}

git archive HEAD --prefix='email_center/' | gzip > ${PATH_DEPLOY}/email_center.tar.gz

cd ${PATH_DEPLOY}


###########################

scp -PPORT email_center.tar.gz deploy@IP:~/
ssh deploy@IP -pPORT 'cd ~/; tar xzvfp email_center.tar.gz '

ssh deploy@IP -pPORT 'cd ~/email_center; pip install -r ./requirements.txt'
echo 'requirements updated'

ssh deploy@IP -pPORT 'cd ~/email_center; export EMAIL_CENTER_CONFIG_TYPE="development"'
echo 'set environment parament'

ssh deploy@IP -pPORT 'cd ~/email_center; ./update-database.sh'
echo 'db updated'

ssh deploy@IP -pPORT 'cd ~/email_center; supervisorctl -c supervisord.conf update'
echo 'supervisor config updated'

ssh deploy@IP -pPORT 'cd ~/email_center; supervisorctl -c supervisord.conf restart all'
echo 'all restart'

#################################

cd ..
rm -rf ${PATH_DEPLOY}