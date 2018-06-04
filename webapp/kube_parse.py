from subprocess import check_output
import re

def is_taint(node):
    cmd = 'kubectl describe node {}'.format(node)
    try:
        res = check_output(cmd.split()).decode('ascii')
    except:
        return 0
    if re.search('NoSchedule', res):
        return 0
    else:
        return 1

def get_busy_worker():
    cmd = "kubectl get pods"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    busy_gpu = 0
    for line in res:
       if re.search('-worker-', line):
           busy_gpu += 1
    return busy_gpu

def get_total_nodes():
    cmd = "kubectl get nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0

    total_nodes = 0
    for line in res:
        m = re.search('(\S+)\s+Ready\s+(\S+)', line)
        if m:
            if m.group(2) == 'master':
                if is_taint(m.group(1)):
                    total_nodes += 1
            else:
                total_nodes += 1
    return total_nodes


def get_gpu_per_node():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0

    for line in res:
        m = re.search('nvidia.com/gpu:\s+(\d+)', line)
        if m:
            return m.group(1)
    return 0

def get_busy_ps():
    cmd = "kubectl get pods"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    busy_cpu = 0
    for line in res:
       if re.search('-ps-', line):
           busy_cpu += 1
    return busy_cpu

if __name__ == '__main__':
    nodes = get_total_nodes()
    print(nodes)
