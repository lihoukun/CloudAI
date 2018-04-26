This documents how AI Cloud help the life-cycle of AI development.

# 0. port forwarding to open web on Mac
```
# ssh keyless to vpn,  take reference to http://www.linuxproblem.org/art_9.html
# install tool autossh, something like brew install autossh
autossh -M 20086 -f -nNT  -L 8001:127.0.0.1:8001 -L 5000:127.0.0.1:5000  -L 8080:127.0.0.1:30080  -L 8888:127.0.0.1:30088 -L 6006:127.0.0.1:30060 ai@1.tcp.ap.ngrok.io -p20100
# now open localhost:5000
``` 

# 1. train a model 

[image](images/home_train.png)

![image](images/trains_train.png)

```
NUM_GPU set to 4, as we have max 4 GPU.
NUM_CPU set to 2, as larger number do no help performance, but only add initialize burden
NUM_EPOCH is float. try it youself. My estimate is 0.01 takes less than 5min. So set it based on your need.
Select 'Start New Training' and select model to 'resnet-training-demo'
Do NOT train two concurrently. Always stop first before train second. 
During demo, repeatly click log for any worker, until you see completion.
Even if it shows complete, still need manual click 'STOP' to kill the rest containers.
```
![image](images/train_new.png)

![image](images/train_train.png)

# 2. Load Tensorboard to evaluate the training
```
pick anyone, and click load
right click tensorboard button,, this may takes 1 min for US side at least.
Note synthetic data do not have much visualization details.
This process could be doen even when there is training jobs on the fly.
```
![image](images/home_tensorboard.png)

![image](images/tensorboard_load.png)

![image](images/tensorboard_open.png)


# 3. (Optional) show all resource in kubernetes
![image](images/home_kube.png)
```
copy token, and open the dahboard button in new window
select token login, and paste the token
```
![image](images/kube_kube.png)

![image](images/kube_login.png)

![image](images/kubeboard.png)

# 5. (Optional) Nginx and Jupyter
`check user guide if you want to demo these two`
![image](images/home_nginx.png)
![image](images/home_jupyter.png)
