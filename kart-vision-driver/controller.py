import pystk
import torch
import numpy as np

def control(aim_point, current_vel):
    """
    Set the Action for the low-level controller
    :param aim_point: Aim point, in screen coordinate frame [-1..1]
    :param current_vel: Current velocity of the kart
    :return: a pystk.Action (set acceleration, brake, steer, drift)
    """
    action = pystk.Action()
    target_vel = 20
    steer_angle = min((np.arctan(abs(aim_point[0]*1.035/aim_point[1]))), 1)
    action.steer = np.sign(aim_point[0]) * steer_angle
    action.brake = False
    action.nitro = False

    if current_vel < target_vel and steer_angle > 0.9:
        action.acceleration = 0.2
    elif current_vel < target_vel and steer_angle > 0.6:
        action.acceleration = 0.65
    elif current_vel < target_vel:
        action.acceleration = 1
        action.nitro = True
    else:
        action.acceleration = 0

    if steer_angle > 0.95:
        action.drift = True
    else:
        action.drift = False

    return action


if __name__ == '__main__':
    from utils import PyTux
    from argparse import ArgumentParser

    def test_controller(args):
        pytux = PyTux()
        for t in args.track:
            steps, how_far = pytux.rollout(t, control, max_frames=1000, verbose=args.verbose)
            print(steps, how_far)
        pytux.close()


    parser = ArgumentParser()
    parser.add_argument('track', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    test_controller(args)
