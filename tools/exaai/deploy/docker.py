import os

def deploy_jupyter():
    os.system("docker container kill exaai-jupyter-notebook")
    os.system("docker container rm exaai-jupyter-notebook")
    cmd = "docker run -e NB_UID={} -e NB_GID={} -e GRANT_SUDO=yes".format(os.environ.get('JUPYTER_UID'), os.environ.get('JUPYTER_GID'))
    cmd += " --name exaai-jupyter-notebook -d -p {}:8888".format(os.environ.get('JUPYTER_PORT'))
    cmd += " -v {}/notebook/work:/home/jovyan/work".format(os.environ.get('GLUSTER_HOST'))
    cmd += " exaai/jupyter-notebook start-notebook.sh --NotebookApp.token=''"
    print(cmd)
    os.system(cmd)

def deploy_nginx():
    os.system("docker container kill exaai-nginx")
    os.system("docker container rm exaai-nginx")
    nginx_gen_conf()
    cmd = "docker run --name exaai-nginx -v {0}:{0} -p {1}:80 -d exaai/nginx:nfs".format(os.environ.get('GLUSTER_HOST'), os.environ.get('NGINX_PORT'))
    print(cmd)
    os.system(cmd)

