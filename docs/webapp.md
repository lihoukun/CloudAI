This documents how to install the AI Cloud management system.
# 0. pre-requisite
```
#install python3
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo yum install -y python36u
sudo yum install -y python36u-pip
sudo yum install -y python36u-devel
sudo ln -s /usr/bin/python3.6 /usr/bin/python3
sudo python3 -m pip install flask flask-wtf pyyaml
```

# 1. download from github
`git clone https://github.com/lihoukun/CloudAI.git`

# 2. deploy the system
```
# write per data center config .sh
source config_<DATA_CENTER>.sh

# deploy all 
./bin/exaai.sh all

# or deploy what is needed
./bin/exaai.sh pv
./bin/exaai.sh kubeboard
./bin/exaai.sh jupyter
./bin/exaai.sh flask
```

# 3. ngrok for http
```
# write ngrok yaml fiel, in US, the file at ~/.ngrok2/ngrok.yml, and the content is below
tunnels:
  ui:
    addr: ibip91:80
    proto: http
    hostname: exaai.ngrok.io
    auth: "exaai:exaai"
  notebook:
    addr: ibip91:30088
    proto: http
    hostname: notebook.exaai.ngrok.io
    auth: "exaai:exaai"
  tensorboard:
    addr: ibip91:30060
    proto: http
    hostname: tensorboard.exaai.ngrok.io
    auth: "exaai:exaai"
  nginx:
    addr: ibip91:30080
    proto: http
    hostname: nginx.exaai.ngrok.io
  kubeboard:
    addr: ibip91:8001
    proto: http
    hostname: kubeboard.exaai.ngrok.io
    auth: "exaai:exaai"

# start ngrok for http
ngrok start --all
```

# 4. open the brower for 'hosname' defined in under 'ui' in ngrok yaml

