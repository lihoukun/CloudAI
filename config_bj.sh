# net disk related
export SHARED_HOST="/mnt/data"
export HOSTPATH_ENABLE="0"
export HOSTPATH_HOST="/mnt"
export HOSTPATH_CONTAINER="/mnt"
export HOSTPATH_GB="1000"
export GLUSTER_ENABLE="1"
export GLUSTER_NAME="gdistvol"
export GLUSTER_IP="2.2.2.151,2.2.2.152,2.2.2.153,2.2.2.154"
export GLUSTER_HOST="/mnt/data"
export GLUSTER_CONTAINER="/mnt/data"
export GLUSTER_GB="1000"
export NFS_ENABLE="0"
export NFS_HOST="/mnt/gnfs"
export NFS_CONTAINER="/mnt/gnfs"
export NFS_SERVER="2.2.2.91"
export NFS_PATH="/mnt/mnt-nvme-lv"
export NFS_GB="1000"

# web app
export FLASK_DEBUG="1"
export FLASK_DB='/home/ai/workspace/sqlite3.db'

# Ports
export NGROK_DOMAIN="exaai.ap.ngrok.io"
