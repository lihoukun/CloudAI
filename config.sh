# net disk related
export NAS_MODE="GLUSTER"
export HOSTPATH_ENABLE="1"
export HOSTPATH_HOST="/nfs"
export HOSTPATH_CONTAINER="/nfs/hostpath"
export HOSTPATH_GB="1000"
export GLUSTER_ENABLE="0"
export GLUSTER_NAME="gdistvol"
export GLUSTER_IP="2.2.2.1,2.2.2.2,2.2.2.3,2.2.2.4"
export GLUSTER_HOST="/nfs/gdv"
export GLUSTER_CONTAINER="/nfs/gdv"
export GLUSTER_GB="1000"
export NFS_ENABLE="0"
export NFS_HOST="/nfs/nvme"
export NFS_CONTAINER="/nfs/nvme"
export NFS_SERVER="2.2.2.91"
export NFS_PATH="/mnt/mnt-nvme-lv"
export NFS_GB="1000"

# web app
export FLASK_DEBUG="1"
export FLASK_APP="main.py"
export FLASK_DB='/home/ai/workspace/sqlite3.db'

# Jupyter notebook
export JUPYTER_UID="1000"
export JUPYTER_GID="1000"

# Ports
export FLASK_PORT="30050"
export KUBEBOARD_PORT="8001"
export TENSORBOARD_PORT="30060"
export NGINX_PORT="30080"
export JUPYTER_PORT="30088"
