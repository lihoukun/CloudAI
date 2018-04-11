import os
import glob

def get_models():
    models = []
    for dirname in glob.glob('/data/models/*'):
        if not os.path.isdir(dirname): continue
        worker_cmd = '{}/worker.sh'.format(dirname)
        ps_cmd = '{}/ps.sh'.format(dirname)
        if not os.path.isfile(worker_cmd): continue
        if not os.path.isfile(ps_cmd): continue
        models.append([os.path.basename(dirname), worker_cmd, ps_cmd])
    return models

def get_trainings():
    trainings = []
    for dirname in glob.glob('/data/train/*'):
        if not os.path.dirname(dirname): continue
        trainings.append(os.path.basename(dirname))
    return trainings
