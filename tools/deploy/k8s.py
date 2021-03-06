import os
import re
from subprocess import check_output

def no_pods():
    cmd = "kubectl get pods"
    try:
        res = check_output(cmd.split()).decode('ascii')
    except:
        print('fail to check pods status')
        return False
    if res:
        print('cannot stop pv when pods are running')
        return False
    else:
        return True

def stop_pv():
    if not no_pods():
        exit(1)

    os.system('kubectl delete pvc --all')
    os.system('kubectl delete pv --all')

def start_pv():
    record_dir = os.path.dirname(os.path.realpath(__file__)) + '/records'
    if not os.path.isdir(record_dir):
        os.makedirs(record_dir, 0o775)

    k8s_file = '{}/k8s_pv.yaml'.format(record_dir)
    if os.path.isfile(k8s_file):
        cmd = 'kubectl delete -f {}'.format(k8s_file)
        print(cmd)
        os.system(cmd)

    k8s_yaml = gen_pv_yaml()
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

    if os.environ.get('NFS_ENABLE') == '1':
        nfs_pv_gb = int(os.environ.get('NFS_GB'))
        nfs_pvc_gb = nfs_pv_gb / 2
        k8s_yaml += """---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: {0}Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  mountOptions:
    - fsc
  nfs:
    path: "{1}"
    server: {3}
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: nfs-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: {2}Gi
  storageClassName: nfs
""".format(nfs_pv_gb, os.environ.get('NFS_HOST'), nfs_pvc_gb, os.environ.get('NFS_SERVER'))

    if os.environ.get('CEPH_ENABLE') == '1':
        ceph_pv_gb = int(os.environ.get('CEPH_GB'))
        ceph_pvc_gb = ceph_pv_gb / 2
        k8s_yaml += """---
apiVersion: v1
kind: Secret
metadata:
  name: ceph-secret
data:
  key: {3}
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ceph-pv
spec:
  capacity:
    storage: {0}Gi
  accessModes:
  - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ceph
  cephfs:
    monitors:
      - {1}
    user: admin
    secretRef:
      name: ceph-secret
    readOnly: false
  mountOptions:
    - fsc
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: ceph-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: {2}Gi
  storageClassName: ceph
""".format(ceph_pv_gb, os.environ.get('CEPH_SERVER'), ceph_pvc_gb, os.environ.get('CEPH_SECRET'))

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

