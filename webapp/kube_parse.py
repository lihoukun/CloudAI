from subprocess import check_output

def get_total_gpu():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        return 0
    max_gpu = 0
    flip = False
    for line in res:
        if flip:
            m = re.search('gpu:\s+(\d)', line)
            if m:
                max_gpu += int(m.group(1))
            flip = False
        else:
            flip = True
            continue
    return max_gpu // 2

def get_busy_gpu():
    pass

def get_total_cpu():
    cmd = "kubectl get nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
        return len(res) - 1
    except:
        return 0

def get_busy_cpu():
    pass