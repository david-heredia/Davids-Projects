from planner import Planner, save_model
import torch
import torch.utils.tensorboard as tb
import numpy as np
from utils import load_data
import dense_transforms

def train(args):
    from os import path
    # check for best device to train on
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device('cpu')

    model = Planner().to(device)
    train_logger = None
    if args.log_dir is not None:
        train_logger = tb.SummaryWriter(path.join(args.log_dir, 'train'))

    # load data
    train_data = load_data(dataset_path='drive_data', batch_size=args.batch_size)

    # define loss and optimizer
    loss_func = torch.nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=14)

    global_step = 0
    for epoch in range(args.num_epochs):
        train_logger.add_scalar('lr', optimizer.param_groups[0]['lr'], global_step=global_step)
        model.train()
        for x_batch, y_batch in train_data:
            # run forward pass and get loss
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)
            output = model(x_batch)
            loss = loss_func(output, y_batch)

            # zero out gradient, run backward pass, and step
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_logger.add_scalar('loss', loss, global_step=global_step)
            log(train_logger, x_batch, y_batch, output, global_step)
            global_step += 1
        scheduler.step()
    save_model(model)

def log(logger, img, label, pred, global_step):
    """
    logger: train_logger/valid_logger
    img: image tensor from data loader
    label: ground-truth aim point
    pred: predited aim point
    global_step: iteration
    """
    import matplotlib.pyplot as plt
    import torchvision.transforms.functional as TF
    fig, ax = plt.subplots(1, 1)
    ax.imshow(TF.to_pil_image(img[0].cpu()))
    WH2 = np.array([img.size(-1), img.size(-2)])/2
    ax.add_artist(plt.Circle(WH2*(label[0].cpu().detach().numpy()+1), 2, ec='g', fill=False, lw=1.5))
    ax.add_artist(plt.Circle(WH2*(pred[0].cpu().detach().numpy()+1), 2, ec='r', fill=False, lw=1.5))
    logger.add_figure('viz', fig, global_step)
    del ax, fig

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--log_dir')
    parser.add_argument('-bs', '--batch_size', type=int, default=64)
    parser.add_argument('-ne', '--num_epochs', type=int, default=20)
    parser.add_argument('-lr', '--learning_rate', type=float, default=0.0005)

    args = parser.parse_args()
    train(args)
