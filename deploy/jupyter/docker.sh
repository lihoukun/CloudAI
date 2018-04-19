docker container kill exaai-jupyter-notebook
docker container rm exaai-jupyter-notebook
docker run --name exaai-jupyter-notebook -d -p 30088:8888 -v /nfs/nvme/notebooks/work:/home/jovyan/work exaai/jupyter-notebook start-notebook.sh --NotebookApp.token=''
