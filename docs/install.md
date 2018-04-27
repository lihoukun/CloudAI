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
# for US side only
source config.sh

# deploy all 
./bin/exaai.sh all

# or deploy what is needed
./bin/exaai.sh pv
./bin/exaai.sh kubeboard
./bin/exaai.sh jupyter
./bin/exaai.sh flask
```

# 3. (Optional) Port Forward in case hosts do not have external IP
```
# install autossh, for MAC
brew install autossh

# port forwarding needed ports
autossh -M 20000 -f -nNT  -L 8001:127.0.0.1:8001 -L 5000:127.0.0.1:5000  -L 8080:127.0.0.1:30080  -L 8888:127.0.0.1:30088 -L 6006:127.0.0.1:30060 USER@HOST -p PORT
```

# 4. Open the browser and enjoy
`curl localhost:5000`
