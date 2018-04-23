The AI Cloud management system will need the below tools to be pre-installed.


# ensure all cloud nodes have datetime sync-ed to internet
```
sudo yum -y install ntp
sudo chkconfig ntpd on
sudo ntpdate pool.ntp.org
sudo service ntpd start
```

# install docker
## remove old version
```
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine
```
## install
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce
```
## add needed group so that docker command no need run as sudo
```
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker
# to takes effect, need logout and re-login
```
## (optional) test if docker works
`docker run hello-world`


# install kubernetes
## add repository
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

## install and config
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

# Install Nvidia GPU docker plugin
## If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
```
docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
sudo yum remove nvidia-docker
```
## Add the package repositories
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | \
  sudo tee /etc/yum.repos.d/nvidia-docker.repo
```
## Install nvidia-docker2 and reload the Docker daemon configuration
```
sudo yum install -y nvidia-docker2
sudo pkill -SIGHUP dockerd
```
## Test nvidia-smi with the latest official CUDA image
```
docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi
```
## config update
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

## enable the change
```
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl restart docker.service
```

================
Create Cluster
================


[Master]
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chmod 666 $HOME/.kube/config
sudo sysctl net.bridge.bridge-nf-call-iptables=1
    * Add the following to /etc/sysctl.conf: net.bridge.bridge-nf-call-iptables=1
    * sudo echo 'net.bridge.bridge-nf-call-iptables=1' >> /etc/sysctl.conf
[flannel]
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.9.1/Documentation/kube-flannel.yml
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.10.0/Documentation/kube-flannel.yml


kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.10/nvidia-device-plugin.yml
# record output for nodes join use, or
# kubeadm token create --print-join-command

[Nodes]
sudo sysctl net.bridge.bridge-nf-call-iptables=1
# change to root, and run what master print
sudo kubeadm join 10.10.10.91:6443 --token unl6a8.ud84g741xmbr45kb --discovery-token-ca-cert-hash sha256:4e594ae2db4b3fde6391b0372393bc508ada36390eecc7dc19ca18a595159252




[DELETE]
Master:
kubectl drain umf --delete-local-data --force --ignore-daemonsets
kubectl delete node umf

Slave:
echo exaai123! |sudo -S kubeadm reset
sudo systemctl stop kubelet
sudo systemctl stop docker
sudo rm -rf /var/lib/cni/
sudo rm -rf /var/lib/kubelet/*
sudo rm -rf /etc/cni/
sudo ifconfig cni0 down
sudo ifconfig flannel.1 down
sudo ifconfig docker0 down
sudo ip link delete cni0
sudo ip link delete flannel.1
sudo systemctl restart docker.service
sudo systemctl start docker
sudo systemctl start kubelet

[ADD]
Master to get command line:
sudo kubeadm token create --print-join-command

Slave to paste:
sudo kubeadm join **** 

[Check Status]
kubectl -n kube-system get all

-------------------------------------------------------------------
[Master]
kubectl drain umf01 --delete-local-data --force --ignore-daemonsets
kubectl drain umf02 --delete-local-data --force --ignore-daemonsets
kubectl drain umf03 --delete-local-data --force --ignore-daemonsets
kubectl drain umf04 --delete-local-data --force --ignore-daemonsets
kubectl drain umf21 --delete-local-data --force --ignore-daemonsets
kubectl drain umf22 --delete-local-data --force --ignore-daemonsets
kubectl drain umf23 --delete-local-data --force --ignore-daemonsets
kubectl drain umf24 --delete-local-data --force --ignore-daemonsets
kubectl delete node umf01
kubectl delete node umf02
kubectl delete node umf03
kubectl delete node umf04
kubectl delete node umf21
kubectl delete node umf22
kubectl delete node umf23
kubectl delete node umf24
#run slave reset part
sudo rm -r $HOME/.kube

Flannel
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sudo sysctl net.bridge.bridge-nf-call-iptables=1
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.10.0/Documentation/kube-flannel.yml

Calico
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sudo sysctl net.bridge.bridge-nf-call-iptables=1
kubectl apply -f https://docs.projectcalico.org/v3.0/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml

kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.10/nvidia-device-plugin.yml
kubectl apply -f ~/workspace/release/CloudAI/deploy/persistent-volume.yaml
kubectl -n kube-system get all

[Slave]
echo exaai123! |sudo -S kubeadm reset
sudo systemctl stop kubelet
sudo systemctl stop docker
sudo rm -rf /var/lib/cni/
sudo rm -rf /var/lib/kubelet/*
sudo rm -rf /etc/cni/
sudo ifconfig cni0 down
sudo ifconfig flannel.1 down
sudo ifconfig docker0 down
sudo ip link delete cni0
sudo ip link delete flannel.1
sudo systemctl restart docker.service
sudo systemctl start docker
sudo systemctl start kubelet

sudo kubeadm join 2.2.2.91:6443 --token vvb0ry.edz0j9l0m0u3xe42 --discovery-token-ca-cert-hash sha256:1159e693c898c05ddd0a5a33d34d33a8485661bfbe626e53bc94a794c100758f

-------------------------------------------------------------------
[NFS]
https://www.58jb.com/html/135.html
  volumes:
    - name: nfs
      nfs:
        # FIXME: use the right hostname
        server: 2.2.2.91
        path: "/mnt/mnt-nvme-lv"

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/storage_administration_guide/s1-nfs-client-config-options

[GlusterFS]
https://github.com/kubernetes/examples/tree/master/staging/volumes/glusterfs
http://k8s.docker8.com/plugins/glusterfs.html


