import argparse
import os
import datetime
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ps_num', help='choose ps number', type=int)
    parser.add_argument('--worker_num', help='choose worker number', type=int)
    parser.add_argument('--gpu_per_node', help='number gpu per node', type=int)
    parser.add_argument('--record_dir', help='record files path')
    parser.add_argument('--log_dir', help='log dir for tensorboard')
    parser.add_argument('--name', help='job name')
    parser.add_argument('--image', help='container image')
    parser.add_argument('--mnt', help='mnt option')
    parser.add_argument('--script', help='script cmd')
    parser.add_argument('--params', help=' hyper params setting')
    args = parser.parse_args()
    return args


def generate_cluster(name, ps_num, worker_num, port):
    if ps_num is None:
        ps_num = 1
    if worker_num is None:
        worker_num = 2

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
    return cluster


def generate_train_configmap(name, cluster, envs):
    ps_hosts_str = ''
    if 'ps' in cluster:
        ps_hosts_str = ','.join(cluster['ps'])

    worker_hosts_str = ''
    if 'worker' in cluster:
        worker_hosts_str = ','.join(cluster['worker'])

    k8s_configmap = """---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {0}-configmap
data:
  PS_HOSTS: "{1}"
  WORKER_HOSTS: "{2}"
""".format(name, ps_hosts_str, worker_hosts_str)

    for k, v in envs.items():
        k8s_configmap += """
  {0}: "{1}"
""".format(k, v)

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
    num_workers = 0
    if 'worker' in cluster:
        num_workers += len(cluster['worker'])

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

    if mnt_option == 'cephfs':
        k8s_job += """
  - name: ceph-volume
    persistentVolumeClaim:
      claimName: ceph-pvc
"""
    elif mnt_option == 'nfs':
        k8s_job += """
  - name: nfs-volume
    persistentVolumeClaim:
      claimName: nfs-pvc
"""
    elif mnt_option == 'gluster':
        k8s_job += """
  - name: gluster-volume
    persistentVolumeClaim:
      claimName: gluster-pvc
"""
    elif mnt_option == 'hostpath':
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

    if mnt_option == 'cephfs':
        k8s_job += """
    - name: ceph-volume
      mountPath: "/mnt/{}"
""".format(os.environ.get('CEPH_CONTAINER'))
    elif mnt_option == 'nfs':
        k8s_job += """
    - name: nfs-volume
      mountPath: "/mnt/{}"
""".format(os.environ.get('NFS_CONTAINER'))
    elif mnt_option == 'gluster':
        k8s_job += """
    - name: gluster-volume
      mountPath: "/mnt/{}"
""".format(os.environ.get('GLUSTER_CONTAINER'))
    elif mnt_option == 'hostpath':
        k8s_job += """
    - name: hostpath-volume
      mountPath: "/mnt/{}"
""".format(os.environ.get('HOSTPATH_CONTAINER'))

    k8s_job += """
    command: ["bash", "-c", "{3}"]
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


def generate_train_config(name, ps_num, worker_num, gpu_per_node, image, mnt_option, script, envs):
    port = 2220
    cluster = generate_cluster(name, ps_num, worker_num, port)

    k8s_config = ''
    k8s_config += generate_train_configmap(name, cluster, envs)
    for job, hosts in cluster.items():
        for i in range(len(hosts)):
            k8s_config += generate_train_service(job, i, port, name)
            k8s_config += generate_train_job(cluster, job, i, port, name, gpu_per_node, image, mnt_option, script)

    return k8s_config


def main():
    args = parse_args()
    envs = {}
    if args.params:
        for k, v in json.loads(args.params).items():
            envs[k] = v
    if args.log_dir:
        envs['LOG_DIR'] = args.log_dir

    k8s_config = generate_train_config(args.name, args.ps_num, args.worker_num,
                                       args.gpu_per_node, args.image, args.mnt, args.script, envs)

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

