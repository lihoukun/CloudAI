# net disk related
export SHARED_HOST="/mnt/nfs1T"
export HOSTPATH_ENABLE="1"
export HOSTPATH_HOST="/mnt/nfs1T"
export HOSTPATH_CONTAINER="/hostpath/nfs1T"
export HOSTPATH_GB="1000"
export GLUSTER_ENABLE="0"
export GLUSTER_NAME="gdistvol"
export GLUSTER_IP="2.2.2.1,2.2.2.2,2.2.2.3,2.2.2.4"
export GLUSTER_HOST="/nfs/gdv"
export GLUSTER_CONTAINER="/nfs/gdv"
export GLUSTER_GB="1000"
export NFS_ENABLE="1"
export NFS_HOST="/mnt/nfs1T"
export NFS_CONTAINER="/mnt/nfs1T"
export NFS_SERVER="2.2.2.4"
export NFS_PATH="/mnt/nfs1T"
export NFS_GB="1000"

# web app
export FLASK_DEBUG="1"
export FLASK_APP="main.py"
export FLASK_DB='/home/ai/workspace/sqlite3.db'

# Jupyter notebook
export JUPYTER_UID="1000"
export JUPYTER_GID="1000"

# NETWORKING
export NGROK_DOMAIN="exaai.ngrok.io"
export FLASK_PORT="5000"
export TENSORBOARD_PORT="30060"
export NGINX_PORT="30080"
export JUPYTER_PORT="30088"
