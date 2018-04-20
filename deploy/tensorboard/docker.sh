docker kill exaai-tensorboard
docker rm exaai-tensorboard
docker run --name exaai-tensorboard -d -p 30060:6006 -v $1:/local/mnt/workspace exaai/tensorboard tensorboard --logdir=/local/mnt/workspace
