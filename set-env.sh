#! /bin/bash

if [ "$EMAIL_CENTER_CONFIG_TYPE" != "production" ]; then
	echo 'export EMAIL_CENTER_CONFIG_TYPE="production"' >> /etc/profile
	source /etc/profile
	echo "set env"
else
	echo "no set"
fi
