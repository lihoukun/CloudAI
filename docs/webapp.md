This documents how to install the AI Cloud management system.
# 0. pre-requisite
```
#install python3
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo yum install -y python36u
sudo yum install -y python36u-pip
sudo yum install -y python36u-devel
sudo ln -s /usr/bin/python3.6 /usr/bin/python3
sudo python3 -m pip install flask flask-wtf pyyaml gunicorn
```

# 1. download from github
```
cd ~
mkdir workspace
cd workspace
git clone https://github.com/lihoukun/CloudAI.git
```

# 2. deploy the system
```
vi config_bj.sh # and update wherever neccessary
source config_bj.sh

# deploy all 
./bin/exaai.sh restart all

# or deploy what is needed
./bin/exaai.sh restart pv
./bin/exaai.sh restart jupyter
./bin/exaai.sh restart web
```

# 3. add cronjobs
```
crontab -e # and add following lines, replacing CloudAI workspace and shared netdrive path if needed

* * * * * python3 /home/ai/workspace/release/CloudAI/tools/cron/train_pend.py /nfs/nvme
* * * * * python3 /home/ai/workspace/release/CloudAI/tools/cron/train_running.py /nfs/nvme
*/5 * * * * python3 /home/ai/workspace/release/CloudAI/tools/cron/train_finished.py /nfs/nvme
0 */3 * * * python3 /home/ai/workspace/release/CloudAI/tools/cron/train_stopped.py /nfs/nvme
```

# 4. ngrok for http
```
# write ngrok yaml fiel, in US, the file at ~/.ngrok2/ngrok.yml, and the content is below
tunnels:
  ui:
    addr: cnumf01:80
    proto: http
    hostname: exaai.ap.ngrok.io
    auth: "exaai:exaai"
  notebook:
    addr: cnumf01:30088
    proto: http
    hostname: notebook.exaai.ap.ngrok.io
    auth: "exaai:exaai"
  tensorboard:
    addr: cnumf01:30060
    proto: http
    hostname: tensorboard.exaai.ap.ngrok.io
    auth: "exaai:exaai"

# start ngrok for http
ngrok start --all
```

# 5. open the browser and visit 'exaai.ap.ngrok.io'

