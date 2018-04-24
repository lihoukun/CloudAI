This documents the needed pre-steps before deploying the AI Cloud management system.

# 1. datetime sync to internet
```
sudo yum -y install ntp
sudo chkconfig ntpd on
sudo ntpdate pool.ntp.org
sudo service ntpd start
```

# 2. install docker
## 2.1 remove old version
```
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine
```
## 2.2. install
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce
```
## 2.3 add docker group for non-root user
```
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker
# to takes effect, need logout and re-login
```
## 2.4 (optional) test if docker works
`docker run hello-world`


# 3. install kubernetes
## 3.1 add repository
```
# US version where google can be visited
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
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
docker run --runtime=nvidia --rm exaai/tf-gpu nvidia-smi
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

