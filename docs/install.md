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
sudo systemctl start docker && \
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
EOF

# China mainland version
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
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

## 3.2 install and config
```
sudo setenforce 0
sudo yum install -y kubelet kubeadm kubectl
sudo systemctl enable kubelet
sudo systemctl start kubelet
sudo sed -i "s/cgroup-driver=systemd/cgroup-driver=cgroupfs/g" /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
sudo systemctl daemon-reload
sudo systemctl restart kubelet

sudo systemctl enable kubelet.service
sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo swapoff -a
```

# 4. Install Nvidia GPU docker plugin
## 4.1 remove old version 
```
docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
sudo yum remove nvidia-docker
```
## 4.2 Add the package repositories
```
# if the curl cmd get hang, simply kill and retry, or direct add the repo
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
  sudo tee /etc/yum.repos.d/nvidia-docker.repo
```
## 4.3 Install and reload configuration
```
sudo yum install -y nvidia-docker2
sudo pkill -SIGHUP dockerd
```
## 4.4 (Optional) test using nvidia-smi
```
docker run --runtime=nvidia exaai/tf-gpu nvidia-smi
docker container prune
```
## 4.5 config update
```
# add default runtime in /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}

# add below env in /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
Environment="KUBELET_EXTRA_ARGS=--feature-gates=DevicePlugins=true"
```

## 4.6 enable the change
```
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl restart docker.service
```

