import os
import glob

def get_models():
    models = []
    for dirname in glob.glob('/nfs/nvme/models/*'):
        if not os.path.isdir(dirname): continue
        cmd = '{}/worker.sh'.format(dirname)
        if not os.path.isfile(cmd): continue
        models.append([os.path.basename(dirname), cmd])
    return models

def get_trainings():
    trainings = []
    for dirname in glob.glob('/nfs/nvme/train/*'):
        if not os.path.dirname(dirname): continue
        trainings.append(os.path.basename(dirname))
    return trainings
