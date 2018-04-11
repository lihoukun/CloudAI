# User Guide

## port forward to localhost. This should one needs get done ONCE!
brew install autossh\n
autossh -M 20000 -f -nNT  -L 8001:127.0.0.1:8001 -L 5000:127.0.0.1:30050  -L 8080:127.0.0.1:30080  -L 8888:127.0.0.1:30088 -L 6006:127.0.0.1:30060 ai@1.tcp.ngrok.io -p22958
curl localhost:5000

## Define your model
All models stored at /data/models, with dirname as the model name
Under each model dir, needs provide a worker.sh and ps.sh for each kubernetes POD to call.
Env variales ['PS_HOSTS', 'WORKER_HOSTS', 'MODEL_NAME', 'POD_NAME', 'SIGNATURE', 'NUM_EPOCH'] is pre-defined.
Must ensure training dir point point to '/data/train/${MODEL_NAME}_${SIGNATURE}'

## Run your model
From localhost:5000, click train, and submit the form.
