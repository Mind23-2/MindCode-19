"""Functions of optimizer"""
import os

from mindspore.nn.optim import AdamWeightDecay
from mindspore.nn.optim.momentum import Momentum

from .schedulers import get_policy


def get_learning_rate(args, batch_num):
    """Get learning rate"""
    return get_policy(args.lr_scheduler)(args, batch_num)


def get_optimizer(args, model, batch_num):
    """Get optimizer for training"""
    print(f"=> When using train_wrapper, using optimizer {args.optimizer}")
    args.start_epoch = int(args.start_epoch)
    optim_type = args.optimizer.lower()
    params = get_param_groups(model)
    learning_rate = get_learning_rate(args, batch_num)
    step = int(args.start_epoch * batch_num)
    train_step = len(learning_rate)
    print(f"=> Get LR from epoch: {args.start_epoch}\n"
          f"=> Start step: {step}\n"
          f"=> Total step: {train_step}")
    learning_rate = learning_rate * int(os.getenv("DEVICE_NUM", args.device_num))

    if optim_type == "momentum":
        optim = Momentum(
            params=params,
            learning_rate=learning_rate,
            momentum=args.momentum,
            weight_decay=args.weight_decay
        )
    elif optim_type == "adamw":
        optim = AdamWeightDecay(
            params=params,
            learning_rate=learning_rate,
            beta1=args.beta[0],
            beta2=args.beta[1],
            eps=args.eps,
            weight_decay=args.weight_decay
        )
    else:
        raise ValueError(f"optimizer {optim_type} is not supported")

    return optim


def get_param_groups(network):
    """ get param groups """
    decay_params = []
    no_decay_params = []
    for x in network.trainable_params():
        parameter_name = x.name
        if parameter_name.endswith(".weight"):
            # Dense or Conv's weight using weight decay
            decay_params.append(x)
        else:
            # all bias not using weight decay
            # bn weight bias not using weight decay, be carefully for now x not include LN
            no_decay_params.append(x)

    return [{'params': no_decay_params, 'weight_decay': 0.0}, {'params': decay_params}]
