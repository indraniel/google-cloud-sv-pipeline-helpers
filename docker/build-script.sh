#!/usr/bin/env bash

apt-get -y install --no-install-recommends \
	           zlib1g \
	           zlib1g-dev \
	           libssl-dev \
               hall-lab-python-3.7.0 \
               git

/opt/hall-lab/python-3.7.0/bin/pip install requests==2.21.0
/opt/hall-lab/python-3.7.0/bin/pip install crcmod==2.21.0
/opt/hall-lab/python-3.7.0/bin/pip install google-auth==1.6.2
/opt/hall-lab/python-3.7.0/bin/pip install google-api-python-client==1.7.8
/opt/hall-lab/python-3.7.0/bin/pip install google-cloud-storage==1.14.0

apt-get clean all
