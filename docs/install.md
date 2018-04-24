This documents how to install the AI Cloud management system.

# 1. download from github
`git clone https://github.com/lihoukun/CloudAI.git`

# 2. deploy the system
```
# check config.yaml file, ensure the values accord with Hardware
# For those of values that needs adjustment, you could either
# a. (Recommended) setup env variables in local. For bash, export EnvName=EnvValue
# b. (Alternatie) directly modify config.yaml
./bin/exaai.sh all
```

# 3. (Optional) Port Forward in case hosts do not have external IP
```
# install autossh, for MAC
brew install autossh

# port forwarding needed ports
autossh -M 20000 -f -nNT  -L 8001:127.0.0.1:8001 -L 5000:127.0.0.1:30050  -L 8080:127.0.0.1:30080  -L 8888:127.0.0.1:30088 -L 6006:127.0.0.1:30060 USER@HOST -p PORT
```