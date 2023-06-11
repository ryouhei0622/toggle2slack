#!/bin/sh
source ~/miniforge3/etc/profile.d/conda.sh
cd ~/code/utilities/ && touch error.log && touch out.log && conda init zsh && conda activate utilities && python toggle2slack.py
