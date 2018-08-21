import argparse
import os
import datetime
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('model', help='choose a model')
    parser.add_argument('flow', help='choose a flow', choices=['train', 'eval', 'serve'])
    parser.add_argument('--ps_num', help='choose ps number', type=int)
    parser.add_argument('--worker_num', help='choose worker number', type=int)
    parser.add_argument('--gpu_per_node', help='number gpu per node', type=int)
    parser.add_argument('--epoch', help='choose worker number', type=float)
    parser.add_argument('--record_dir', help='record files path')
    parser.add_argument('--signature', help='signature label')
    parser.add_argument('--image', help='container image')
    args = parser.parse_args()
    return args

def generate_cluster(model, signature, ps_num, worker_num, port):
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
    cluster['chief'] = []
    cluster['ps'] = []
    cluster['worker'] = []
    for i in range(ps_num):
        ps_host = '{}-{}-ps-{}.default.svc.cluster.local:{}'.format(model, signature, i, port)
        cluster['ps'].append((ps_host))
    for i in range(worker_num):
        worker_host = '{}-{}-worker-{}.default.svc.cluster.local:{}'.format(model, signature, i, port)
        cluster['worker'].append(worker_host)
    for i in range(chief_num):
        chief_host = '{}-{}-chief-{}.default.svc.cluster.local:{}'.format(model, signature, i, port)
        cluster['chief'].append(chief_host)

    return cluster

def generate_train_configmap(model, signature, cluster, epoch):
    ps_hosts_str = ','.join(cluster['ps'])
    combined_worker_hosts = cluster['worker'] + cluster['chief']
    worker_hosts_str = ','.join(combined_worker_hosts)

    k8s_configmap = """---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {0}-{1}-configmap
data:
  PS_HOSTS: "{2}"
  WORKER_HOSTS: "{3}"
  NUM_EPOCH: "{4}"
  MODEL_NAME: "{0}"
  SIGNATURE: "{1}"
""".format(model, signature, ps_hosts_str, worker_hosts_str, epoch)
    return k8s_configmap

def generate_train_service(job, id, port, model, signature):
    k8s_service = """---
apiVersion: v1
kind: Service
metadata:
  name: {3}-{4}-{0}-{1}
  labels:
    model: {3}
    signature: s{4}
spec:
  type: ClusterIP
  ports:
  - port: {2}
    targetPort: {2}
    protocol: TCP
  selector:
    job: {0}
    task: t{1}
    model: {3}
    signature: s{4}
""".format(job, id, port, model, signature)
    return k8s_service

def generate_train_job(cluster, job, id, port, model, signature, record_dir, gpu_per_node, image):
    tf_config = {}
    tf_config['cluster'] = cluster
    tf_config['task'] = {'type': job, 'index': id}

    k8s_job = """---
apiVersion: v1
kind: Pod
metadata:
  name: {2}-{3}-{0}-{1}
  labels:
    job: {0}
    task: t{1}
    model: {2}
    signature: s{3}
spec:
  restartPolicy: OnFailure
  volumes:
""".format(job, id, model, signature)

    if os.environ.get('NFS_ENABLE') == '1':
        k8s_job += """
  - name: nfs-volume
    nfs:
      server: "{}"
      path: "{}"
""".format(os.environ.get('NFS_SERVER'), os.environ.get('NFS_PATH'))
    if os.environ.get('GLUSTER_ENABLE') == '1':
        k8s_job += """
  - name: gluster-volume
    persistentVolumeClaim:
      claimName: gluster-pvc
"""
    if os.environ.get('HOSTPATH_ENABLE') == '1':
        k8s_job += """
  - name: hostpath-volume
    persistentVolumeClaim:
      claimName: hostpath-pvc
"""
    k8s_job += """
  containers:
  - name: tf-training
    image: {2}
    securityContext:
      privileged: true
    envFrom:
    - configMapRef:
        name: {0}-{1}-configmap
    volumeMounts:
""".format(model, signature, image)

    if os.environ.get('NFS_ENABLE') == '1':
        k8s_job += """
    - name: nfs-volume
      mountPath: "{}"
""".format(os.environ.get('NFS_CONTAINER'))
    if os.environ.get('GLUSTER_ENABLE') == '1':
        k8s_job += """
    - name: gluster-volume
      mountPath: "{}"
""".format(os.environ.get('GLUSTER_CONTAINER'))
    if os.environ.get('HOSTPATH_ENABLE') == '1':
        k8s_job += """
    - name: hostpath-volume
      mountPath: "{}"
""".format(os.environ.get('HOSTPATH_CONTAINER'))

    k8s_job += """
    command: ["/bin/bash"]
    args: ["{3}/tensorflow.sh"]
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
      value: "{4}"
""".format(job, id, port, record_dir, json.dumps(tf_config))

    if job == 'ps':
        k8s_job += """
    - name: CUDA_VISIBLE_DEVICES
      value: " "
    resources:
      requests:
        cpu: "4"
        memory: 16Gi
      limits:
        cpu: "6"
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

def generate_train_config(model, signature, ps_num, worker_num, epoch, record_dir, gpu_per_node, image):
    port = 2220
    cluster = generate_cluster(model, signature, ps_num, worker_num, port)

    k8s_config = ''
    k8s_config += generate_train_configmap(model, signature, cluster, epoch)
    for job, hosts in cluster.items():
        for i in range(len(hosts)):
            k8s_config += generate_train_service(job, i, port, model, signature)
            k8s_config += generate_train_job(job, i, port, model, signature, record_dir, gpu_per_node, image)

    return k8s_config

def main():
    args = parse_args()
    k8s_config = ''
    signature = args.signature if args.signature else datetime.datetime.now().strftime("%y%m%d%H%M%S")
    epoch = args.epoch if args.epoch else 1.0
    if args.flow == 'train':
        k8s_config = generate_train_config(args.model, signature, args.ps_num, args.worker_num, epoch, args.record_dir, args.gpu_per_node, args.image)
    elif args.flow == 'eval':
        k8s_config = generate_eval_config(args.model, signature)
    else:
        pass

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

