import torch
import torch.nn.functional as F
from torchvision.transforms import functional as TF


def spatial_argmax(logit):
    """
    Compute the soft-argmax of a heatmap
    :param logit: A tensor of size BS x H x W
    :return: A tensor of size BS x 2 the soft-argmax in normalized coordinates (-1 .. 1)
    """
    weights = F.softmax(logit.view(logit.size(0), -1), dim=-1).view_as(logit)
    return torch.stack(((weights.sum(1) * torch.linspace(-1, 1, logit.size(2)).to(logit.device)[None]).sum(1),
                        (weights.sum(2) * torch.linspace(-1, 1, logit.size(1)).to(logit.device)[None]).sum(1)), 1)

class doubleBlock(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        super().__init__()
        self.block = torch.nn.Sequential(
            torch.nn.Conv2d(input_channels, output_channels, kernel_size=3, padding=1, stride=1, bias=False),
            torch.nn.BatchNorm2d(output_channels),
            torch.nn.ReLU(),
            torch.nn.Conv2d(output_channels, output_channels, kernel_size=3, padding=1, stride=1, bias=False),
            torch.nn.BatchNorm2d(output_channels),
            torch.nn.ReLU()
        )

    def forward(self, x):
        return self.block(x)

class downBlock(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        super().__init__()
        self.block = torch.nn.Sequential(
            torch.nn.Conv2d(input_channels, input_channels, kernel_size=3, stride=2, padding=1),
            doubleBlock(input_channels, output_channels)
        )
    def forward(self, x):
        return self.block(x)

class upBlock(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        super().__init__()
        self.up = torch.nn.ConvTranspose2d(input_channels, output_channels, kernel_size=2, stride=2)
        self.double_conv = doubleBlock(input_channels, output_channels)

    def forward(self, x, skip):
        x = self.up(x)
        if x.size() != skip.size():
            x = TF.resize(x, skip.size()[2:])
        x = torch.cat([skip, x], dim=1)
        return self.double_conv(x)

class Planner(torch.nn.Module):
    def __init__(self, input_channels=3, output_channels=1, int_channels=[32,64,128]):
        super().__init__()

        i = int_channels[0]
        self.first_double = doubleBlock(input_channels, i)

        # initialize list of down blocks
        self.down_blocks = torch.nn.ModuleList()
        for c in int_channels[1:]:
            self.down_blocks.append(downBlock(i, c))
            i = c

        # initialize bottom of unet
        self.bottom = torch.nn.Sequential(
            doubleBlock(int_channels[-1], 2*int_channels[-1]),
        )

        # initialize list of up blocks
        self.up_blocks = torch.nn.ModuleList()
        for c in reversed(int_channels):
            self.up_blocks.append(upBlock(2 * c, c))

        # final convolution
        self.last_conv = torch.nn.Conv2d(int_channels[0], output_channels, kernel_size=1)

    def forward(self, img):
        """
        Predict the aim point in image coordinate, given the supertuxkart image
        @img: (B,3,96,128)
        return (B,2)
        """
        skip_connections = []
        x = self.first_double(img)
        skip_connections.append(x)

        # loop through down blocks
        for down_block in self.down_blocks:
            x = down_block(x)
            skip_connections.insert(0, x)

        # bottom layer of unet
        x = self.bottom(x)

        # loop through up blocks
        for i, up_block in enumerate(self.up_blocks):
            skip = skip_connections[i]
            x = up_block(x, skip)

        # final output convolution
        x = self.last_conv(x)

        # get spatial argmax
        x = spatial_argmax(x.squeeze(1))
        return x


def save_model(model):
    from torch import save
    from os import path
    if isinstance(model, Planner):
        return save(model.state_dict(), path.join(path.dirname(path.abspath(__file__)), 'planner.th'))
    raise ValueError("model type '%s' not supported!" % str(type(model)))


def load_model():
    from torch import load
    from os import path
    r = Planner()
    r.load_state_dict(load(path.join(path.dirname(path.abspath(__file__)), 'planner.th'), map_location='cpu'))
    return r


if __name__ == '__main__':
    from controller import control
    from utils import PyTux
    from argparse import ArgumentParser


    def test_planner(args):
        # Load model
        planner = load_model().eval()
        pytux = PyTux()
        for t in args.track:
            steps, how_far = pytux.rollout(t, control, planner=planner, max_frames=1000, verbose=args.verbose)
            print(steps, how_far)
        pytux.close()


    parser = ArgumentParser("Test the planner")
    parser.add_argument('track', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    test_planner(args)
