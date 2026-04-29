#!/usr/bin/env bash
run_experiment() {
    # 시드 반복 실행
    for sd in 1 2 3 4 
    do
        mpiexec --oversubscribe -n ${n_clients} python run_exp_main.py \
                --dataset=${dataset} \
                --algorithm=${algorithm} \
                --seed=${sd} \
                --partition_type=${partition_type} \
                --n_clients=${n_clients} \
                --n_client_data=${n_client_data} \
                --model_type=${model_type} \
                --use_private_SGD=${use_private_SGD} \
                --noise_multiplier=${noise_multiplier} \
                --l2_norm_clip=${l2_norm_clip} \
                --optimizer=${optimizer} \
                --lr=${lr} \
                --dml_weight=${dml_weight} \
                --alpha=${alpha} \
                --beta=${beta} \
                --film_max_t=${film_max_t} \
                --film_min_t=${film_min_t} \
                --pruning_threshold=${pruning_threshold} \
                --major_percent=${major_percent} \
                --n_epochs=${n_epochs} \
                --n_rounds=${n_rounds} \
                --batch_size=${batch_size} \
                --verbose=${verbose} \
                --semantic_enable=${semantic_enable} \
                --snr_db=${snr_db} \
                --compressed_dim=${compressed_dim} \
                --device=${device} \
                --channel_type=${channel_type}
    done

    # # 결과 플로팅
    # python plot.py --dataset=${dataset} \
    #             --partition_type=${partition_type} \
    #             --n_clients=${n_clients} \
    #             --n_client_data=${n_client_data} \
    #             --use_private_SGD=${use_private_SGD} \
    #             --optimizer=${optimizer} \
    #             --lr=${lr} \
    #             --noise_multiplier=${noise_multiplier} \
    #             --l2_norm_clip=${l2_norm_clip} \
    #             --private_model_type=${private_model_type} \
    #             --proxy_model_type=${proxy_model_type} \
    #             --dml_weight=${dml_weight} \
    #             --alpha=${alpha} \
    #             --beta=${beta} \
    #             --major_percent=${major_percent} \
    #             --batch_size=${batch_size} \
    #             --n_epochs=${n_epochs} \
    #             --n_rounds=${n_rounds} \
    #             --entropy_threshold=${entropy_threshold}
}

n_epochs=1
use_private_SGD=0
noise_multiplier=1.0
l2_norm_clip=1.0

lr=0.001
optimizer='adam'

verbose=1
dml_weight=0.5
alpha=0.5
beta=0.001

# CIFAR10 - CNN
# dataset='cifar10'
# partition_type='class'
# n_rounds=200
# model_type='resnet'
# n_client_data=5000
# n_clients=9
# batch_size=250

dataset='cifar10' #'mnist' #'cifar10', 'fashion-mnist'
partition_type='class'
n_rounds=200
model_type='resnet'
n_client_data=3000
n_clients=9
batch_size=100

# dataset='mnist' #fashion-mnist
# partition_type='class'
# n_rounds=200
# model_type='resnet'
# n_client_data=5000
# n_clients=9
# batch_size=250
film_max_t=0.8
film_min_t=0.3
# partition_type='iid'
pruning_threshold=1.0
device=0
compressed_dim=64
beta=0.001
snr_db=12
for channel_type in 'awgn' 'rayleigh' #'rayleigh' #'awgn'  #'rayleigh' # 'awgn' 
do
    for dataset in 'cifar10' #'cifar100' #'fashion-mnist' 
    do
        for major_percent in 0.7
        do
            for algorithm in 'SSFLv6' 'SC-USFL' 'SFL' #'SSFLv6' #$'SSFLv6' 'SC-USFL' 'SFL' #  'SSFLv6_w_o_vib' 'SSFLv6_w_o_film' #'SSFLv5_w_o_vib' 'SSFLv5_w_o_beta''FL'  #'SSFLv6' 'SSFLv5' #'SSFL_w_o_vib' 'SSFL_w_o_film' 'SSFLv4' 'SC-USFL' 'FL' #'SSFL_w_o_vib' 'SSFL_w_o_film' 'SSFL_w_o_film' 'SSFL_w_o_beta' #'SSFLv4' 'FL' 'SC-USFL' 'SFL' # 'SSFL_w_o_vib' 'SSFL_w_o_film' 'SSFL_w_o_beta' # 'SC-USFL' 'SFL' 'SSFLv4'  # #'SSFLv4' #'SSFLv5' # 'SSFL_w_o_beta' 'SSFL_w_o_vib' 
            do
                if [ "$algorithm" == "SSFLv6" ]; then
                    semantic_enable=1
                    model_type=resnetv2
                    n_epochs=1
                    snr_db=12
                    compressed_dim=4096

                # #     # Phase 1: FiLM은 현재 최고 세팅(0.8, 0.3)으로 고정
                #     film_max_t=0.7
                #     film_min_t=0.4

                #     # Beta를 로그 스케일로 강력하게 탐색
                #     for beta in 0.1 0.05 0.01 0.005 0.001
                #     do
                #         # Beta가 강해질수록 KL이 낮아지므로 Threshold도 맞춰서 낮춰봄
                #         for pruning_threshold in 1.5 1.0 0.5
                #         do
                #             run_experiment
                #         done
                #     done

                    
                    # # Phase 1에서 찾은 불변의 황금 세팅 고정!
                    for pruning_threshold in 1.0 # 1.5
                    do
                        # Beta는 0.01을 메인으로 하되, 0.005도 살짝 걸쳐서 확인
                        for beta in 0.01 # 0.005
                        do
                            # FiLM Max T (최악 채널 문턱): 0.8(유지) vs 0.9(극한 통신 절감)
                            for film_max_t in 0.7
                            do
                                # FiLM Min T (최상 채널 문턱): 0.2(성능 부스트) vs 0.3(유지) vs 0.4(통신 절감)
                                for film_min_t in 0.4
                                do
                                    run_experiment
                                done
                            done
                        done
                    done
                elif [ "$algorithm" == "SSFLv6_w_o_vib" ]; then
                    semantic_enable=1
                    # n_epochs=1
                    model_type=resnetv2
                    n_epochs=1
                    pruning_threshold=1.0
                    for i in 3  #0.005 0.01 #0.001 
                    do
                        if [ "$i" == 1 ]; then
                            beta=0.1
                            compressed_dim=64
                        elif [ "$i" == 2 ]; then
                            beta=0.01
                            compressed_dim=128
                        else
                            beta=0.005
                            film_max_t=0.8
                            film_min_t=0.3
                            compressed_dim=4096
                        fi
                        run_experiment
                    done
                elif [ "$algorithm" == "SSFLv6_w_o_film" ]; then
                    semantic_enable=1
                    semantic_enable=1
                    # n_epochs=1
                    model_type=resnetv2
                    n_epochs=1
                    pruning_threshold=1.0
                    for i in 3  #0.005 0.01 #0.001 
                    do
                        if [ "$i" == 1 ]; then
                            beta=0.1
                            compressed_dim=64
                        elif [ "$i" == 2 ]; then
                            beta=0.01
                            compressed_dim=128
                        else
                            beta=0.005
                            film_max_t=0.8
                            film_min_t=0.3
                            compressed_dim=4096
                        fi
                        run_experiment
                    done





                elif [ "$algorithm" == "SC-USFL" ]; then
                    semantic_enable=1
                    model_type=resnet
                    n_epochs=1
                    pruning_threshold=1.0
                    film_max_t=0.8
                    film_min_t=0.3
                    for beta in 0.001 #0.005 0.01 #0.001 
                    do
                        for compressed_dim in 1352
                        do
                            run_experiment
                        done
                    done
                elif [ "$algorithm" == "SC-USFL_SCM" ]; then
                    semantic_enable=1
                    model_type=resnet
                    n_epochs=1
                    for beta in 0.001 
                    do
                        for compressed_dim in 1352
                        do
                            run_experiment
                        done
                    done
                elif [ "$algorithm" == "SFL" ]; then
                    semantic_enable=0
                    compressed_dim=64
                    n_epochs=1
                    snr_db=12
                    pruning_threshold=1.0
                    film_max_t=0.8
                    film_min_t=0.3
                    run_experiment
                elif [ "$algorithm" == "FL" ]; then
                    semantic_enable=0
                    compressed_dim=64
                    n_epochs=1
                    snr_db=12
                    pruning_threshold=1.0
                    run_experiment
                fi
            done
        done
    done
done