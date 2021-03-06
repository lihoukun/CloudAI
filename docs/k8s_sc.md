This documents the steps to set up or tear down k8s cluster.

# 1. Create Cluster from Scratch
```
# on all nodes, run
sudo sysctl net.bridge.bridge-nf-call-iptables=1
sudo swapoff -a
# make above permanent
sudo vi /etc/fstab #comment out line with swap
sudo vi /etc/sysctl.conf # add new line: net.bridge.bridge-nf-call-iptables=1

# Run below steps on the master node
# reference to https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/ for future change
sudo kubeadm init --pod-network-cidr=192.168.0.0/16

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/rbac-kdd.yaml
kubectl apply -f https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calico-networking/1.7/calico.yaml
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
sudo ifconfig tunl0 down
sudo ip link delete tunl0
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
