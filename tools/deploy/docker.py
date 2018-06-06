import os

def stop_jupyter():
    os.system("docker container kill exaai-jupyter-notebook")
    os.system("docker container rm exaai-jupyter-notebook")

def start_jupyter():
    cmd = "docker run -e NB_UID={} -e NB_GID={} -e GRANT_SUDO=yes".format(os.environ.get('JUPYTER_UID'), os.environ.get('JUPYTER_GID'))
    cmd += " --name exaai-jupyter-notebook -d -p {}:8888".format(os.environ.get('JUPYTER_PORT'))
    cmd += " -v {}/notebook/work:/home/jovyan/work".format(os.environ.get('SHARED_HOST'))
    cmd += " exaai/jupyter-notebook start-notebook.sh --NotebookApp.token=''"
    print(cmd)
    os.system(cmd)

