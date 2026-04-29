#!/usr/bin/env bash

n_epochs=1
use_private_SGD=0
noise_multiplier=1.0
l2_norm_clip=1.0

lr=0.001
optimizer='adam'

major_percent=0.1
dml_weight=0.5
alpha=0.5
beta=0.5
verbose=1

# # CIFAR10
dataset='cifar10'
partition_type='class'
n_rounds=200
private_model_type='CNN2'
proxy_model_type='CNN1_classifier'
n_client_data=1000
n_clients=8
batch_size=250

# MNIST and Fashion-MNIST
# dataset='mnist'  # 'fashion-mnist'
# partition_type='class'
# n_rounds=200
# private_model_type='CNN2'
# proxy_model_type='CNN1_classifier'
# n_clients=8
# n_client_data=1000
# batch_size=250


python plot_test.py --dataset=${dataset} \
            --partition_type=${partition_type} \
            --n_clients=${n_clients} \
            --n_client_data=${n_client_data} \
            --use_private_SGD=${use_private_SGD} \
            --optimizer=${optimizer} \
            --lr=${lr} \
            --noise_multiplier=${noise_multiplier} \
            --l2_norm_clip=${l2_norm_clip} \
            --private_model_type=${private_model_type} \
            --proxy_model_type=${proxy_model_type} \
            --dml_weight=${dml_weight} \
            --alpha=${alpha} \
            --beta=${beta} \
            --major_percent=${major_percent} \
            --batch_size=${batch_size} \
            --n_epochs=${n_epochs} \
            --n_rounds=${n_rounds}