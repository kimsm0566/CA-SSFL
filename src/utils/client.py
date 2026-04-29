import torch
import torch.nn as nn
from models.model import ClientResNet18v1, ClientResNet18v2, ServerResNet18, ServerResNet18v2, AWGNChannel, ResNet18_FL, RayleighChannel

def client_init_model(args):
    if args.algorithm == 'SFL':
        return ClientResNet18v1(args)
    elif args.algorithm == 'FL':
        return ResNet18_FL(args)
    elif args.algorithm == 'SSFLv4' or args.algorithm == 'SSFLv5'or args.algorithm == 'SSFLv5_w_o_vib'or args.algorithm == 'SSFLv5_w_o_beta' or args.algorithm == 'SSFLv6' or args.algorithm == 'SSFLv6_w_o_vib' or args.algorithm == 'SSFLv6_w_o_vib_fair' or args.algorithm == 'SSFLv6_w_o_film' or args.algorithm == 'SSFLv6_w_o_beta':
        return ClientResNet18v2(args)
    elif args.algorithm == 'SC-USFL' or args.algorithm == 'SC-USFL_SCM':
        return ClientResNet18v2(args)
    raise ValueError(f"Unknown model type: {args.model_type}")

def server_init_model(args):
    if args.algorithm == 'FL':
        return ResNet18_FL(args)
    if args.algorithm == 'SFL' or args.algorithm == 'SC-USFL' or args.algorithm == 'SC-USFL_SCM':
        return ServerResNet18(args)
    elif args.algorithm == 'SSFLv4' or args.algorithm == 'SSFLv5'or args.algorithm == 'SSFLv5_w_o_vib'or args.algorithm == 'SSFLv5_w_o_beta' or args.algorithm == 'SSFLv6' or args.algorithm == 'SSFLv6_w_o_vib' or args.algorithm == 'SSFLv6_w_o_vib_fair' or args.algorithm == 'SSFLv6_w_o_film' or args.algorithm == 'SSFLv6_w_o_beta':
        return ServerResNet18v2(args)
    raise ValueError(f"Unknown model type: {args.model_type}")

def init_optimizer(model, args):
    if args.optimizer == 'sgd':
        return torch.optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=5e-4)
    elif args.optimizer == 'adam':
        return torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    raise ValueError(f"Unknown optimizer: {args.optimizer}")

def init_optimizer(model, args):
    if args.optimizer == 'sgd':
        return torch.optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=5e-4)
    elif args.optimizer == 'adam':
        return torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-4)
    raise ValueError(f"Unknown optimizer: {args.optimizer}")

class Client(nn.Module):
    def __init__(self, data, private_test_data, args, rank):
        super(Client, self).__init__()
        self.idx = rank
        self.args = args
        self.device = args.device
        self.data = data # Train Dataset
        self.private_test_data = private_test_data
        
        # 모델 및 채널 초기화
        self.model = client_init_model(args).to(self.device)
        self.optimizer = init_optimizer(self.model, args)
        if args.channel_type == 'awgn':
            self.channel = AWGNChannel(snr_db =args.snr_db).to(args.device)
        elif args.channel_type == 'rayleigh':
            self.channel = RayleighChannel(snr_db =args.snr_db).to(args.device) 
        
       


class Server(nn.Module):
    def __init__(self, data, args, rank):
        super(Server, self).__init__() # 상속 수정
        self.idx = rank
        self.args = args
        self.device = args.device
        self.test_data = data # Test Dataset
        
        # 모델 초기화
        self.model = server_init_model(args).to(self.device)
        # Aggregation 및 평가를 위한 Global Client Model
        self.global_client_model = client_init_model(args).to(self.device)
        
        self.optimizer = init_optimizer(self.model, args)
        
