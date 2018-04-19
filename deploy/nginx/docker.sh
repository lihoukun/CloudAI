docker container kill exaai-nginx
docker container rm exaai-nginx
docker run --name exaai-nginx -v /nfs:/nfs -p 30080:80 -d exaai/nginx:nfs
