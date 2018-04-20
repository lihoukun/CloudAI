FROM exaai/tf-gpu:latest
RUN groupadd -r -g 1000 ai && useradd -d /home/ai -ms /bin/bash -r -u 1000 -g ai ai
USER ai
WORKDIR /home/ai
