This documents the needed tools seup.

# 0 pre-requisites
## 0.1 install
`# install nvidia driver and ai superuser account`

## 0.2 check
```
# nvidia driver
nvidia-smi
# check ai user account has UID 1000, and GID(ai) 1000
id
```

# 1 input sudo password, and set sudo never expire during install
## 1.1 install
`sudo sh -c 'echo "Defaults timestamp_timeout=-1" | (EDITOR="tee -a" visudo)'`
## 1.2 check
`# by command 'sudo visudo', will see last line have timout set to -1`

# 2 datetime sync to internet
## 2.1 install
```
sudo yum -y install ntp && \
sudo chkconfig ntpd on && \
sudo ntpdate pool.ntp.org && \
sudo service ntpd start
```
## 2.2 check
```#type 'date' to verify```

# 3 install docker
## 3.1 install
```
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine && \
sudo yum install -y yum-utils device-mapper-persistent-data lvm2 && \
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && \
sudo yum install -y docker-ce && \
sudo usermod -aG docker $USER && \
sudo systemctl enable docker && \
sudo systemctl start docker
```
## 3.2 check
`# logout and login again, then run 'docker run hello-world' `


# 4 install kubernetes
## 4.1 install
```
# US version where google can be visited
cat <<EOF | sudo tee -a /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF

# China mainland version
cat <<EOF | sudo tee -a /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
        http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```
```
sudo setenforce 0 && \
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes && \
sudo systemctl enable kubelet && \
sudo systemctl start kubelet && \
sudo systemctl stop firewalld && \
sudo systemctl disable firewalld && \
sudo swapoff -a
```

# 5 Install Nvidia GPU docker plugin
## 5.1 install 
```
docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f && \
sudo yum remove nvidia-docker
```
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
  sudo tee /etc/yum.repos.d/nvidia-docker.repo
```
```
sudo yum install -y nvidia-docker2 && \
sudo pkill -SIGHUP dockerd
```

```
# add default runtime in /etc/docker/daemon.json
sudo rm -f /etc/docker/daemon.json && \
cat <<EOF | sudo tee -a /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF 
```
```
sudo systemctl daemon-reload && \
sudo systemctl restart kubelet && \
sudo systemctl restart docker.service
```

