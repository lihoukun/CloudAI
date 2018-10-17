import argparse
import os
import datetime
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ps_num', help='choose ps number', type=int)
    parser.add_argument('--worker_num', help='choose worker number', type=int)
    parser.add_argument('--gpu_per_node', help='number gpu per node', type=int)
    parser.add_argument('--epoch', help='choose worker number', type=int)
    parser.add_argument('--record_dir', help='record files path')
    parser.add_argument('--name', help='job name')
    parser.add_argument('--image', help='container image')
    parser.add_argument('--mnt', help='mnt option')
    parser.add_argument('--script', help='script cmd')
    args = parser.parse_args()
    return args


def generate_cluster(name, ps_num, worker_num, port):
    if ps_num is None:
        ps_num = 2

    if worker_num is None:
        worker_num = 2
        chief_num = 1
    else:
        if worker_num >= 1:
            chief_num = 1
            worker_num -= 1
        else:
            chief_num = 0
            worker_num = 0

    cluster = {}
    if ps_num > 0:
        cluster['ps'] = []
        for i in range(ps_num):
            ps_host = '{}-ps-{}.default.svc.cluster.local:{}'.format(name, i, port)
            cluster['ps'].append((ps_host))
    if worker_num > 0:
        cluster['worker'] = []
        for i in range(worker_num):
            worker_host = '{}-worker-{}.default.svc.cluster.local:{}'.format(name, i, port)
            cluster['worker'].append(worker_host)
    if chief_num > 0:
        cluster['chief'] = []
        for i in range(chief_num):
            chief_host = '{}-chief-{}.default.svc.cluster.local:{}'.format(name, i, port)
            cluster['chief'].append(chief_host)

    return cluster


def generate_train_configmap(name, cluster, epoch):
    ps_hosts_str = ''
    if 'ps' in cluster:
        ps_hosts_str = ','.join(cluster['ps'])

    worker_hosts_str = ''
    if 'worker' in cluster:
        worker_hosts_str = ','.join(cluster['worker'])
    if 'chief' in cluster:
        if worker_hosts_str != '':
            worker_hosts_str += ',' + ','.join(cluster['chief'])
        else:
            worker_hosts_str = ','.join(cluster['chief'])

    k8s_configmap = """---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {0}-configmap
data:
  PS_HOSTS: "{1}"
  WORKER_HOSTS: "{2}"
  NUM_EPOCH: "{3}"
""".format(name, ps_hosts_str, worker_hosts_str, epoch)
    return k8s_configmap


def generate_train_service(job, id, port, name):
    k8s_service = """---
apiVersion: v1
kind: Service
metadata:
  name: {3}-{0}-{1}
  labels:
    name: {3}
spec:
  type: ClusterIP
  ports:
  - port: {2}
    targetPort: {2}
    protocol: TCP
  selector:
    job: {0}
    task: t{1}
    name: {3}
""".format(job, id, port, name)
    return k8s_service


def generate_train_job(cluster, job, id, port, name, gpu_per_node, image, mnt_option, script):
    tf_config = {}
    tf_config['cluster'] = cluster
    tf_config['task'] = {'type': job, 'index': id}
    job_name, job_id = job, id
    if job == 'chief':
        job_name = 'worker'
        if 'worker' in cluster:
            job_id = len(cluster['worker']) + id
    num_workers = 0
    if 'worker' in cluster:
        num_workers += len(cluster['worker'])
    if 'chief' in cluster:
        num_workers += len(cluster['chief'])

    k8s_job = """---
apiVersion: v1
kind: Pod
metadata:
  name: {2}-{0}-{1}
  labels:
    job: {0}
    task: t{1}
    name: {2}
spec:
  restartPolicy: OnFailure
  volumes:
""".format(job, id, name)

    if mnt_option == 'CEPH':
        k8s_job += """
  - name: ceph-volume
    persistentVolumeClaim:
      claimName: ceph-pvc
"""
    elif mnt_option == 'NFS':
        k8s_job += """
  - name: nfs-volume
    persistentVolumeClaim:
      claimName: nfs-pvc
"""
    elif mnt_option == 'GLUSTER':
        k8s_job += """
  - name: gluster-volume
    persistentVolumeClaim:
      claimName: gluster-pvc
"""
    elif mnt_option == 'HOSTPATH':
        k8s_job += """
  - name: hostpath-volume
    persistentVolumeClaim:
      claimName: hostpath-pvc
"""

    k8s_job += """
  containers:
  - name: tf-training
    image: {1}
    securityContext:
      privileged: true
    envFrom:
    - configMapRef:
        name: {0}-configmap
    volumeMounts:
""".format(name, image)

    if mnt_option == 'CEPH':
        k8s_job += """
    - name: ceph-volume
      mountPath: "{}"
""".format(os.environ.get('CEPH_CONTAINER'))
    elif mnt_option == 'NFS':
        k8s_job += """
    - name: nfs-volume
      mountPath: "{}"
""".format(os.environ.get('NFS_CONTAINER'))
    elif mnt_option == 'GLUSTER':
        k8s_job += """
    - name: gluster-volume
      mountPath: "{}"
""".format(os.environ.get('GLUSTER_CONTAINER'))
    elif mnt_option == 'HOSTPATH':
        k8s_job += """
    - name: hostpath-volume
      mountPath: "{}"
""".format(os.environ.get('HOSTPATH_CONTAINER'))

    k8s_job += """
    command: ["{3}"]
    ports:
    - name: tf-training-ports
      containerPort: {2}
      protocol: TCP
      name: http
    env:
    - name: JOB_NAME
      value: {0}
    - name: TASK_ID
      value: "{1}"
    - name: TF_CONFIG
      value: '{4}'
    - name: NUM_WORKERS
      value: '{5}'
""".format(job_name, job_id, port, script, json.dumps(tf_config), num_workers)

    if job == 'ps':
        k8s_job += """
    - name: CUDA_VISIBLE_DEVICES
      value: " "
    resources:
      requests:
        cpu: "8"
        memory: 16Gi
      limits:
        cpu: "12"
        memory: 32Gi
"""
    else:
        k8s_job += """
    resources:
      requests:
        cpu: "6"
        memory: 32Gi
        nvidia.com/gpu: {0}
      limits:
        cpu: "8"
        memory: 48Gi
        nvidia.com/gpu: {0}
""".format(gpu_per_node)

    return k8s_job


def generate_train_config(name, ps_num, worker_num, epoch, gpu_per_node, image, mnt_option, script):
    port = 2220
    cluster = generate_cluster(name, ps_num, worker_num, port)

    k8s_config = ''
    k8s_config += generate_train_configmap(name, cluster, epoch)
    for job, hosts in cluster.items():
        for i in range(len(hosts)):
            k8s_config += generate_train_service(job, i, port, name)
            k8s_config += generate_train_job(cluster, job, i, port, name, gpu_per_node, image, mnt_option, script)

    return k8s_config


def main():
    args = parse_args()
    epoch = args.epoch if args.epoch else 1
    k8s_config = generate_train_config(args.name, args.ps_num, args.worker_num, epoch,
                                       args.gpu_per_node, args.image, args.mnt, args.script)

    if args.record_dir:
        if not os.path.isdir(args.record_dir):
            umask = os.umask(0)
            os.makedirs(args.record_dir, 0o777)
            os.umask(umask)
        cfg_file = '{}/train.yaml'.format(args.record_dir)
        with open(cfg_file, 'w+') as f:
            f.write(k8s_config)
        print("Yaml config generated at {}".format(cfg_file))
    else:
        print(k8s_config)


if __name__ == "__main__":
    main()

