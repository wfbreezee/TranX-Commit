#!/bin/bash
set -e

seed=${1:-0}
vocab="/home/jiang/tranX/data/commit/vocab.freq23.bin"
train_file="/home/jiang/tranX/data/commit/train3.bin"
dropout=0.5
hidden_size=256
embed_size=128
action_embed_size=128
field_embed_size=32
type_embed_size=32
lr_decay=0.985
lr_decay_after_epoch=20
max_epoch=100
patience=1000   # disable patience since we don't have dev set
beam_size=5
batch_size=32
lr=0.0025
ls=0.1
lstm='lstm'
model_name=model.jobs.sup.${lstm}.hid${hidden_size}.embed${embed_size}.act${action_embed_size}.field${field_embed_size}.type${type_embed_size}.drop${dropout}.lr_decay${lr_decay}.lr_dec_aft${lr_decay_after_epoch}.beam${beam_size}.$(basename ${vocab}).$(basename ${train_file}).pat${patience}.max_ep${max_epoch}.batch${batch_size}.lr${lr}.glorot.no_par_info.no_copy.ls${ls}.seed${seed}

echo "**** Writing results to logs/jobs/${model_name}.log ****"
mkdir -p logs/jobs
echo commit hash: `git rev-parse HEAD` > logs/jobs/${model_name}.log

python -u /home/jiang/tranX/exp.py \
    \
    --seed ${seed} \
    --mode train \
    --batch_size ${batch_size} \
    --asdl_file /home/jiang/tranX/asdl/lang/commit/commit_asdl_AT1.txt \
    --transition_system committest \
    --train_file ${train_file} \
    --vocab ${vocab} \
    --lstm ${lstm} \
    --primitive_token_label_smoothing ${ls} \
    --no_parent_field_type_embed \
    --no_parent_production_embed \
    --no_parent_field_embed \
    --no_parent_state \
    --hidden_size ${hidden_size} \
    --embed_size ${embed_size} \
    --action_embed_size ${action_embed_size} \
    --field_embed_size ${field_embed_size} \
    --type_embed_size ${type_embed_size} \
    --dropout ${dropout} \
    --patience ${patience} \
    --max_epoch ${max_epoch} \
    --lr ${lr} \
    --no_copy \
    --lr_decay ${lr_decay} \
    --lr_decay_after_epoch ${lr_decay_after_epoch} \
    --decay_lr_every_epoch \
    --glorot_init \
    --beam_size ${beam_size} \
    --decode_max_time_step 55 \
    --log_every 50 \
    --save_all_models \
    --save_to /home/jiang/tranX/saved_models/jobs/${model_name} 2>&1 | tee -a logs/jobs/${model_name}.log

. /home/jiang/tranX/scripts/commit/test.sh /home/jiang/tranX/saved_models/jobs/${model_name}.bin 2>&1 | tee -a logs/jobs/${model_name}.log
