import argparse
import os
import yaml
from subprocess import check_output

from lib.k8s import deploy_pv, deploy_kubeboard
from lib.flask import deploy_web
from lib.docker import deploy_jupyter, deploy_nginx

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='choose a flow', choices=['flask', 'info'])
    args = parser.parse_args()
    return args

def get_config():
    cfg_yaml = os.path.dirname(os.path.realpath(__file__)) + '/../config.yaml'
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


def deploy_all():
    deploy_one('pv')
    deploy_one('kubeboard')
    deploy_one('jupyter')
    deploy_one('nginx')
    deploy_one('web')

def deploy_one(target):
    if target == 'pv':
        deploy_pv()
    elif target == 'web':
        deploy_web()
    elif target == 'jupyter':
        deploy_jupyter()
    elif target == 'nginx':
        deploy_nginx()
    elif target == 'kubeboard':
        deploy_kubeboard()

def check_k8s():
    cmd = "kubectl describe nodes"
    try:
        res = check_output(cmd.split()).decode('ascii').split('\n')
    except:
        print('Error: kubecl not working!')
        exit(1)
   print('Checking k8s...Done!')

def main():
    config = get_config()
    args = parse_args()
    list_info(config)
    if args.target != 'info':
        check_k8s()
        if args.target == 'all':
            deploy_all()
        else:
            deploy_one(args.target)

if __name__ == "__main__":
    main()