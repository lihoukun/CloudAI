import argparse
import os
import yaml

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
        os.environ[k] = v
        print("ENV '{}' is set to '{}'".format(k, v))

def deploy_flask():
    pass

def deploy(target):
    if target == 'flask':
        deploy_flask()
    elif target == 'all':
        deploy_flask()

def main():
    config = get_config()
    args = parse_args()
    list_info(config)
    if args.target != 'info':
        deploy(args.target)

if __name__ == "__main__":
    main()