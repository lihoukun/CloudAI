docker start exaai-jupyter-notebook || docker run --name exaai-jupyter-notebook -d -p 30088:8888 -v /data/notebooks:/home/jovyan/work exaai/jupyter-notebook start-notebook.sh --NotebookApp.token=''
