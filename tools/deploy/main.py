import argparse
import os
import yaml
from subprocess import check_output

from k8s import start_pv, stop_pv
from flask import start_web, stop_web
from docker import start_jupyter, stop_jupyter

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='choose an action', choices=['start', 'stop', 'restart'])
    parser.add_argument('target', help='choose a target', choices=['pv', 'web', 'jupyter', 'all'])
    args = parser.parse_args()
    return args

def get_config():
    cfg_yaml = os.path.dirname(os.path.realpath(__file__)) + '/../../config.yaml'
    with open(cfg_yaml, 'r') as f:
        lookup = yaml.load(f)
        return lookup

def list_info(config):
    print("ExaAI environment settings:")
    for k, v in config.items():
        if os.environ.get(k):
            print("ENV '{}' is pre-defined to '{}".format(k, os.environ[k]))
        else:
            os.environ[k] = v
            print("ENV '{}' is set to '{}'".format(k, v))


def deploy_all(action):
    deploy_one(action, 'pv')
    deploy_one(action, 'jupyter')
    deploy_one(action, 'web')

def deploy_one(action, target):
    if target == 'pv':
        if action == 'start':
            start_pv()
        elif action == 'stop':
            stop_pv()
        else:
            stop_pv()
            start_pv()
    elif target == 'web':
        if action == 'start':
            start_web()
        elif action == 'stop':
            stop_web()
        else:
            stop_web()
            start_web()
    elif target == 'jupyter':
        if action == 'start':
            start_jupyter()
        elif action == 'stop':
            stop_jupyter()
        else:
            stop_jupyter()
            start_jupyter()

def check_k8s():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        print('Error: kubectl not working!')
        exit(1)
    print('Checking k8s...Done!')

def main():
    config = get_config()
    args = parse_args()
    list_info(config)
    check_k8s()
    if args.target == 'all':
        deploy_all(args.action)
    else:
        deploy_one(args.action, args.target)


if __name__ == "__main__":
    main()
