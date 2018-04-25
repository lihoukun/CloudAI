This documents the steps to set up or tear down k8s cluster.
# 0. (China only) Prepare images fron google
```
# on master nodes:
docker pull exaai/kube-proxy-amd64:v1.10.1
docker pull exaai/kube-scheduler-amd64:v1.10.1
docker pull exaai/kube-apiserver-amd64:v1.10.1
docker pull exaai/kube-controller-manager-amd64:v1.10.1
docker pull exaai/etcd-amd64:3.1.12
docker pull exaai/kubernetes-dashboard-amd64:v1.8.3
docker pull exaai/k8s-dns-dnsmasq-nanny-amd64:1.14.8
docker pull exaai/k8s-dns-sidecar-amd64:1.14.8
docker pull exaai/k8s-dns-kube-dns-amd64:1.14.8
docker pull exaai/pause-amd64:3.1

docker tag exaai/kube-proxy-amd64:v1.10.1 k8s.gcr.io/kube-proxy-amd64:v1.10.1
docker tag exaai/kube-scheduler-amd64:v1.10.1 k8s.gcr.io/kube-scheduler-amd64:v1.10.1
docker tag exaai/kube-apiserver-amd64:v1.10.1 k8s.gcr.io/kube-apiserver-amd64:v1.10.1
docker tag exaai/kube-controller-manager-amd64:v1.10.1 k8s.gcr.io/kube-controller-manager-amd64:v1.10.1
docker tag exaai/etcd-amd64:3.1.12 k8s.gcr.io/etcd-amd64:3.1.12
docker tag exaai/kubernetes-dashboard-amd64:v1.8.3 k8s.gcr.io/kubernetes-dashboard-amd64:v1.8.3
docker tag exaai/k8s-dns-dnsmasq-nanny-amd64:1.14.8 k8s.gcr.io/k8s-dns-dnsmasq-nanny-amd64:1.14.8
docker tag exaai/k8s-dns-sidecar-amd64:1.14.8 k8s.gcr.io/k8s-dns-sidecar-amd64:1.14.8
docker tag exaai/k8s-dns-kube-dns-amd64:1.14.8 k8s.gcr.io/k8s-dns-kube-dns-amd64:1.14.8
docker tag exaai/pause-amd64:3.1 k8s.gcr.io/pause-amd64:3.1

# on slave nodes:
docker pull exaai/kube-proxy-amd64:v1.10.1
docker pull exaai/pause-amd64:3.1
docker pull exaai/kubernetes-dashboard-amd64:v1.8.3

docker tag exaai/kubernetes-dashboard-amd64:v1.8.3 k8s.gcr.io/kubernetes-dashboard-amd64:v1.8.3
docker tag exaai/kube-proxy-amd64:v1.10.1 k8s.gcr.io/kube-proxy-amd64:v1.10.1
docker tag exaai/pause-amd64:3.1 k8s.gcr.io/pause-amd64:3.1

```

# 1. Create Cluster from Scratch
```
# on all nodes, run
sudo sysctl net.bridge.bridge-nf-call-iptables=1
sudo swapoff -a

# Run below steps on the master node
# if US master
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
# if China master
sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --kubernetes-version=v1.10.1

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://docs.projectcalico.org/v3.0/getting-started/kubernetes/installation/hosted/kubeadm/1.7/calico.yaml
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.10/nvidia-device-plugin.yml
# the output of the init command will be used for slave join, which can be got by
kubeadm token create --print-join-command
```

# 2. add slave nodes to cluster
```
# run the command from master's output, which looks like below
sudo kubeadm join 10.10.10.91:6443 --token unl6a8.ud84g741xmbr45kb --discovery-token-ca-cert-hash sha256:4e594ae2db4b3fde6391b0372393bc508ada36390eecc7dc19ca18a595159252
```

# 3. Remove one node from cluster
```
# on master node
kubectl drain <NODE_NAME> --delete-local-data --force --ignore-daemonsets
kubectl delete node <NODE_NAME>

# on slave node
sudo kubeadm reset
sudo systemctl stop kubelet
sudo systemctl stop docker
sudo rm -rf /var/lib/cni/
sudo rm -rf /var/lib/kubelet/*
sudo rm -rf /etc/cni/
sudo ifconfig docker0 down
sudo systemctl restart docker.service
sudo systemctl start docker
sudo systemctl start kubelet
```

# 4. tear down whole cluster
```
# first remove all slave nodes, then remove master nodes as above, and then
rm -r $HOME/.kube
```
# 5. check status 
```
# check all nodes' container is up and running
kubectl -n kube-system get all

# ensure GPU and other resources are recognized
kubectl describe node <NODE_NAME>
```
