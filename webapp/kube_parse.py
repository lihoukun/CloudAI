from subprocess import check_output
import re

def get_total_gpu():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    max_gpu = 0
    flip = False
    for line in res:
        m = re.search('gpu:\s+(\d)', line)
        if m:
            if flip:
                max_gpu += int(m.group(1))
                flip = False
            else:
                flip = True
    return max_gpu

def get_busy_gpu():
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

def get_total_cpu():
    cmd = "kubectl get nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
        return len(res) - 1
    except:
        return 0

def get_busy_cpu():
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

