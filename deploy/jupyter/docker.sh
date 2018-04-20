docker container kill exaai-jupyter-notebook
docker container rm exaai-jupyter-notebook
docker run -e NB_UID=1000 -e NB_GID=1000 -e GRANT_SUDO=yes --name exaai-jupyter-notebook -d -p 30088:8888 -v /nfs/nvme/notebook/work:/home/jovyan/work exaai/jupyter-notebook start-notebook.sh --NotebookApp.token=''
