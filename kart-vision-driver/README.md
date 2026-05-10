# Vision-Based Autonomous Kart Driver

> This project was completed as part of a master's course in deep learning.

## Overview

This project implements an autonomous driver for SuperTuxKart, an open-source kart racing game. A neural network learns to predict where the kart should aim on screen from raw camera images, and a separate heuristic controller translates that aim point into low-level driving actions (steering, acceleration, drift, nitro).

## Process

### 1. Data Collection
Training data was collected by running a rule-based controller on multiple tracks with added noise. At each timestep, the game engine projects a target point 15 units ahead on the track path into screen space. This (image, aim-point) pair is saved as the training example. Noise is injected into the aim point and velocity to improve robustness.

### 2. Model Training
A U-Net encoder-decoder network is trained to regress the 2D aim-point from 96×128 RGB frames. The encoder progressively downsamples through strided convolutions; the decoder upsamples with skip connections from the encoder to recover spatial precision. The final layer produces a heatmap, and a soft-argmax operation converts it to a single normalized (x, y) coordinate. The model is trained with MSE loss using the AdamW optimizer.

### 3. Controller
A lightweight heuristic controller maps the predicted aim point and current velocity to kart actions. Steering is computed via inverse tangent of the aim-point offset. Acceleration is modulated based on velocity and turning angle, with drift enabled for sharp turns and nitro for straight-line speed.

### 4. Evaluation
The trained planner and controller completed full laps on the following tracks:

| Track | Time |
|---|---|
| Zengarden | < 50s |
| Lighthouse | < 50s |
| Hacienda | < 60s |
| Snowtuxpeak | < 60s |
| Cornfield Crossing | < 70s |
| Scotland | < 70s |

> **Note:** The trained model weights (`.th` file) are not included in this repository to prevent academic dishonesty by current or future students of the course.

## Tools Used

- **Modeling:** PyTorch, torchvision
- **Game Engine:** PySuperTuxKart (`pystk`)
- **Logging:** TensorBoard
- **Visualization:** Matplotlib, NumPy
