"""
PyTorch Neural Network architecture for intent classification.
A 3-layer Feedforward Neural Network (Multilayer Perceptron).
"""

import torch
import torch.nn as nn


class NeuralNet(nn.Module):
    """
    Feedforward Neural Network for text intent classification.
    Takes a bag-of-words representation vector and outputs unnormalized class logits.
    """

    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out