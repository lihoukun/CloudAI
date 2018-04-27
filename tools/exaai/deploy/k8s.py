import os
from subprocess import Popen

def deploy_kubeboard():
    os.system("ps aux |grep 'kubectl proxy' |awk '{print $2}' |head -n 1 | xargs kill")
    os.system("kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml")
    yaml_file = os.path.dirname(os.path.realpath(__file__)) + '/../../cfg_files/kubeboard_admin.yaml'
    os.system("kubectl apply -f {}".format(yaml_file))
    Popen(['kubectl', 'proxy'])

def deploy_pv():
    k8s_yaml = gen_pv_yaml()
    record_dir = os.path.dirname(os.path.realpath(__file__)) + '/records'
    if not os.path.isdir(record_dir):
        os.makedirs(record_dir, 0o775)
    k8s_file = '{}/k8s_pv.yaml'.format(record_dir)
    if os.path.isfile(k8s_file):
        cmd = 'kubectl delete -f {}'.format(k8s_file)
        print(cmd)
        os.system(cmd)

    with open(k8s_file, 'w+') as f:
        f.write(k8s_yaml)
    cmd = 'kubectl apply -f {}'.format(k8s_file)
    print(cmd)
    os.system(cmd)
    print('k8s pv deployed')

def gen_pv_yaml():
    k8s_yaml = ""
    if os.environ.get('HOSTPATH_ENABLE') == '1':
        hostpath_pv_gb = int(os.environ.get('HOSTPATH_GB'))
        hostpath_pvc_gb = hostpath_pv_gb / 2
        k8s_yaml += """---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: hostpath-pv
spec:
  capacity:
    storage: {0}Gi
  accessModes:
  - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: hostpath
  hostPath:
    path: "{1}"
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: hostpath-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: {2}Gi
  storageClassName: hostpath
""".format(hostpath_pv_gb, os.environ.get('HOSTPATH_HOST'), hostpath_pvc_gb)

    if os.environ.get('GLUSTER_ENABLE') == '1':
        gluster_pv_gb = int(os.environ.get('GLUSTER_GB'))
        gluster_pvc_gb = gluster_pv_gb / 2
        gluster_ips = os.environ.get('GLUSTER_IP').split(',')
        k8s_yaml += """---
apiVersion: v1
kind: Endpoints
metadata:
  name: glusterfs-cluster
subsets:
"""
        for gluster_ip in gluster_ips:
            k8s_yaml += """ 
- addresses:
  - ip: {}
  ports:
  - port: 1
""".format(gluster_ip)

        k8s_yaml += """---
kind: Service
apiVersion: v1
metadata:
  name: glusterfs-cluster
spec:
  ports:
  - port: 1
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: gluster-pv
spec:
  capacity:
    storage: {0}Gi
  accessModes:
  - ReadWriteMany
  glusterfs:
    endpoints: "glusterfs-cluster"
    path: "{1}"
    readOnly: false
  storageClassName: gluster
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: gluster-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: {2}Gi
  storageClassName: gluster
""".format(gluster_pv_gb, os.environ.get('GLUSTER_NAME'), gluster_pvc_gb)

    return k8s_yaml

