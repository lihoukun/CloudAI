from subprocess import check_output
import re

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
        return len(res) - 3
    except:
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

