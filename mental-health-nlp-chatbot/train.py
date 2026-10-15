"""
Training script for the Mental Health NLP Chatbot.
Processes intents.json, constructs Bag-of-Words training sets,
trains the PyTorch NeuralNet classifier, and exports data.pth.
"""

from pathlib import Path
import json
import random
import time
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from nltk_utils import bag_of_words, tokenize, stem
from model import NeuralNet


class ChatDataset(Dataset):
    """PyTorch Dataset wrapper for Bag-of-Words vectors and class label indices."""

    def __init__(self, x_data: np.ndarray, y_data: np.ndarray):
        self.n_samples = len(x_data)
        self.x_data = x_data
        self.y_data = y_data

    def __getitem__(self, index: int):
        return self.x_data[index], self.y_data[index]

    def __len__(self) -> int:
        return self.n_samples


def train_model(
    intents_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    num_epochs: int = 500,
    batch_size: int = 8,
    learning_rate: float = 0.001,
    hidden_size: int = 16,
    seed: int = 42,
) -> Path:
    """
    Train intent classification model on intents dataset and save checkpoints.
    """
    base_dir = Path(__file__).resolve().parent
    if intents_path is None:
        intents_path = base_dir / "intents.json"
    if output_path is None:
        output_path = base_dir / "data.pth"

    # Set random seeds for reproducibility
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    print("=" * 60)
    print("Mental Health NLP Chatbot - Training")
    print("=" * 60)
    print(f"Loading intents from: {intents_path}")

    with open(intents_path, "r", encoding="utf-8") as f:
        intents = json.load(f)

    all_words = []
    tags = []
    xy = []

    # Loop through each sentence in intents patterns
    for intent in intents["intents"]:
        tag = intent["tag"]
        tags.append(tag)
        for pattern in intent["patterns"]:
            tokens = tokenize(pattern)
            all_words.extend(tokens)
            xy.append((tokens, tag))

    # Stem, lowercase, and filter punctuation
    ignore_words = ["?", ".", "!", ",", ";", ":", "-", "_", "(", ")"]
    all_words = [stem(w) for w in all_words if w not in ignore_words]
    all_words = sorted(set(all_words))
    tags = sorted(set(tags))

    print(f"Total training patterns : {len(xy)}")
    print(f"Total intent classes    : {len(tags)}")
    print(f"Unique vocabulary words : {len(all_words)}")

    # Create training data arrays
    X_train = []
    y_train = []
    for pattern_sentence, tag in xy:
        bag = bag_of_words(pattern_sentence, all_words)
        X_train.append(bag)
        label = tags.index(tag)
        y_train.append(label)

    X_train = np.array(X_train, dtype=np.float32)
    y_train = np.array(y_train, dtype=np.int64)

    input_size = len(X_train[0])
    output_size = len(tags)

    dataset = ChatDataset(X_train, y_train)
    train_loader = DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training device         : {device}")

    model = NeuralNet(input_size, hidden_size, output_size).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    start_time = time.time()
    last_loss = 0.0

    print("-" * 60)
    for epoch in range(num_epochs):
        for words, labels in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)

            # Forward pass
            outputs = model(words)
            loss = criterion(outputs, labels)

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        last_loss = loss.item()
        if (epoch + 1) % 50 == 0 or (epoch + 1) == num_epochs:
            print(f"Epoch [{epoch + 1:3d}/{num_epochs}] - Loss: {last_loss:.4f}")

    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"Training completed in {elapsed:.2f}s | Final Loss: {last_loss:.4f}")

    # Prepare model artifact package
    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "all_words": all_words,
        "tags": tags,
    }

    torch.save(data, str(output_path))
    print(f"Model saved successfully to: {output_path}")
    print("=" * 60)
    return output_path


if __name__ == "__main__":
    train_model()