ps aux |grep 'kubectl proxy' |awk '{print $2}' |head -n 1 | xargs kill
kubectl apply -f dashboard-admin.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
kubectl proxy &>/dev/null &
