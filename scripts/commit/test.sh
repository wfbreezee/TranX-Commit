#!/bin/bash

model_name=$(basename $1)

python /home/jiang/tranX/exp.py \
     \
    --mode test \
    --load_model $1 \
    --beam_size 5 \
    --test_file /home/jiang/tranX/data/commit/test3.bin \
    --decode_max_time_step 55
