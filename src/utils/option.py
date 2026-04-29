import argparse

def args_parser():
    parser = argparse.ArgumentParser()
    
    #Model, algorithm compressed_dim
    parser.add_argument("--algorithm", help="Algorithm: ['SSFL'].",
                        type=str, choices=['SFL', 'SSFLv4', 'SSFLv5', 'SSFLv6', 'SSFLv5_w_o_beta', 'SSFLv5_w_o_vib', 'SSFLv6_w_o_beta', 'SSFLv6_w_o_vib', 'SSFLv6_w_o_vib_fair', 'SSFLv6_w_o_film', 'SC-USFL', 'SC-USFL_SCM','FL'], default="SSFL")
    parser.add_argument("--model_type", help="model architecture.",
                        type=str, choices=['resnet', 'resnetv2'], default="resnet")
    parser.add_argument("--channel_type", help="model architecture.",
                        type=str, choices=['awgn', 'rayleigh'], default="resnet")

    #Data
    parser.add_argument("--dataset", help="Name of the dataset: [mnist, fashion-mnist, cifar10].",
                        type=str, choices=['mnist', 'fashion-mnist', 'cifar10', 'cifar100'], default="mnist")
    parser.add_argument("--partition_type", help="Name of the dataset: [iid, class, class-rep].",
                        type=str, choices=['iid', 'class', 'class-rep'], default="iid")
    parser.add_argument("--private_test_data_size", help="private_test_data_size", type=int, default=1000)
    
    #path
    parser.add_argument("--result_path", help="Where to save results.", type=str, default="./results")
    parser.add_argument("--data_path", help="Where to find the data.", type=str, default="./datasets")
    
    #Hyper parameter
    parser.add_argument('--pruning_threshold', type=float, default=0.1)
    parser.add_argument('--beta', type=float, default=0.1)
    parser.add_argument('--compressed_dim', type=int, default=256)
    parser.add_argument('--semantic_enable', type=int, default=1, help="1 is enable 0 : don't use semantic")
    parser.add_argument('--snr_db', type=int, default=10, help="Channel SNR in dB")
    parser.add_argument("--n_clients", help="Number of clients.", type=int, default=2)
    parser.add_argument("--use_private_SGD", help="[int as bool] Use private SGD or not.", type=int, default=1)
    parser.add_argument("--n_client_data", help="Number of data points for each client.", type=int, default=1000)
    parser.add_argument("--optimizer", help="Optimizer.", type=str, default='adam')
    parser.add_argument("--lr", help="Learning rate.", type=float, default=0.001)
    parser.add_argument("--af", help="aggregation frequency.", type=int, default=1)
    parser.add_argument("--momentum", help="Momentum for SGD.", type=float, default=0.9)
    
    parser.add_argument("--dml_weight", help="DML weight.", type=float, default=0.5)
    parser.add_argument("--major_percent", help="Percentage of majority class for client data partition.", type=float, default=0.8)
    parser.add_argument("--noise_multiplier", help="Gaussian noise deviation for DP SGD.", type=float, default=1.0)
    parser.add_argument("--l2_norm_clip", help="L2 norm maximum for clipping in DP SGD.", type=float, default=1.0)
    parser.add_argument("--n_epochs", help="Number of DML epochs.", type=int, default=3)
    parser.add_argument("--n_rounds", help="Number of FL rounds.", type=int, default=300)
    parser.add_argument("--batch_size", help="Batch size during training.", type=int, default=250)
    parser.add_argument("--alpha", help="Batch size during training.", type=float, default=0.5)
    parser.add_argument('--film_max_t', type=float, default=0.8, help='Max FiLM threshold for worst SNR')
    parser.add_argument('--film_min_t', type=float, default=0.3, help='Min FiLM threshold for best SNR')
    parser.add_argument('--channel_mask_allpass_enable', type=int, default=0,
                        help='Force the final SNR-conditioned channel mask to pass all latent dimensions while keeping encoder FiLM gating intact.')
    parser.add_argument('--semantic_spreading_enable', type=int, default=0,
                        help='Enable DCT-based spreading over selected active semantic features before transmission.')
    parser.add_argument('--snr_adaptive_beta_enable', type=int, default=0,
                        help='Scale beta by (1 - normalized_snr) during SSFLv6 training.')
    parser.add_argument('--semantic_power_enable', type=int, default=0,
                        help='Enable KL-aware semantic power allocation on active features before transmission.')
    parser.add_argument('--semantic_power_alpha', type=float, default=2.0,
                        help='Softmax temperature scale for KL-aware semantic power allocation.')
    parser.add_argument('--latent_mixing_enable', type=int, default=0,
                        help='Enable encoder-side residual latent mixing before VIB heads.')
    parser.add_argument('--latent_mixing_strength', type=float, default=0.0,
                        help='Residual scaling factor for encoder-side latent mixing.')
    parser.add_argument('--latent_mixing_groups', type=int, default=8,
                        help='Grouped 3x3 mixer groups for encoder-side latent mixing.')
    parser.add_argument('--encoder_downsample_enable', type=int, default=0,
                        help='Enable stride-2 encoder downsampling followed by projection back to compressed_dim.')
    parser.add_argument('--encoder_downsample_mode', type=str, default='stride2_proj',
                        choices=['stride2_proj'],
                        help='Encoder downsampling variant to use.')
    parser.add_argument('--encoder_downsample_proj_dim', type=int, default=4096,
                        help='Hidden projection dimension used after encoder downsampling bottleneck.')
    parser.add_argument('--semidense_enable', type=int, default=0,
                        help='Enable group-balanced semi-dense support selection with the same active budget K.')
    parser.add_argument('--semidense_group_size', type=int, default=16,
                        help='Group size used by semi-dense support balancing over the 4096-D latent.')
    parser.add_argument('--semidense_group_topk', type=int, default=4,
                        help='Preferred per-group top-k when semi-dense support balancing is enabled.')
    parser.add_argument('--support_floor_enable', type=int, default=0,
                        help='Enable low-SNR minimum support floor after base mask construction.')
    parser.add_argument('--support_floor_min_active', type=int, default=256,
                        help='Minimum number of active dimensions to keep when low-SNR support floor is triggered.')
    parser.add_argument('--support_floor_snr_db', type=float, default=0.0,
                        help='Apply support floor only when the sampled training SNR is at or below this dB threshold.')
    parser.add_argument('--importance_repetition_enable', type=int, default=0,
                        help='Duplicate a small set of the most important active features into auxiliary transmit slots.')
    parser.add_argument('--importance_repetition_topk', type=int, default=32,
                        help='Number of top-important active features to duplicate when repetition is enabled.')
    parser.add_argument('--base_refinement_enable', type=int, default=0,
                        help='Use a two-tier support composed of always-on base support plus refinement support.')
    parser.add_argument('--base_refinement_variable_enable', type=int, default=0,
                        help='Keep base support fixed by VIB importance and choose refinement support with an SNR-aware variable budget.')
    parser.add_argument('--base_refinement_semantic_aware_enable', type=int, default=0,
                        help='Reimplement variable refinement so base is constrained by semantic mask and refinement uses a semantic-aware mixed score.')
    parser.add_argument('--base_support_k', type=int, default=128,
                        help='Number of always-on base support features in the base+refinement scheme.')
    parser.add_argument('--refinement_support_k', type=int, default=128,
                        help='Number of additional refinement support features in the base+refinement scheme.')
    parser.add_argument('--refinement_semantic_weight', type=float, default=0.5,
                        help='Weight of semantic score in semantic-aware refinement mixed scoring.')
    parser.add_argument('--refinement_channel_weight', type=float, default=0.5,
                        help='Weight of channel score in semantic-aware refinement mixed scoring.')
    parser.add_argument('--csi_source_mask_enable', type=int, default=0,
                        help='Fuse source statistics with SNR when generating the FiLM mask.')
    parser.add_argument('--server_feature_impute_enable', type=int, default=0,
                        help='Enable a small residual feature denoiser/imputer before server-side semantic decoding.')
    parser.add_argument('--mpi_trace_enable', type=int, default=0,
                        help='Enable lightweight rank-level MPI trace logs around SSFLv6 blocking send/recv points.')
    parser.add_argument('--fair_vib_reference_topk', type=int, default=256,
                        help='Reference top-k budget used by fair w/o VIB proxy selection when pruning_threshold=1.0.')
    # parser.add_argument("--beta", help="Batch size during training.", type=float, default=0.5)
    #utils
    parser.add_argument("--device", help="Which cuda device to use.", type=int, default=0)
    parser.add_argument("--seed", help="Random seed.", type=int, default=0)
    parser.add_argument("--verbose", help="Verbose level.", type=int, default=0)
    
    args = parser.parse_args()
    return args
