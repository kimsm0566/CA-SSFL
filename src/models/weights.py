import torch

def extract_numpy_weights(model):

    tensor_weights = model.state_dict()
    numpy_weights = {}

    for k in tensor_weights.keys():
        numpy_weights[k] = tensor_weights[k].detach().cpu().numpy()

    return numpy_weights


def convert_np_weights_to_tensor(weights):

    for k in weights.keys():
        weights[k] = torch.from_numpy(weights[k])

    return weights