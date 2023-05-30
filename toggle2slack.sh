#!/bin/sh
source ~/miniforge3/etc/profile.d/conda.sh
cd ~/code/utilities/ && conda init zsh && conda activate utilities && python toggle2slack.py
