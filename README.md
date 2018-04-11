# User Guide

# port forward to localhost. This should one needs get done ONCE!
1. install autossh
  brew install autossh
2. port forwarding
autossh -M 20000    -nNT -L 8001:127.0.0.1:8001 -L 5000:127.0.0.1:30050 -L 8080:127.0.0.1:30080 -L 8888:127.0.0.1:30088 -L 6006:127.0.0.1:30060
3. open localhost:5000

