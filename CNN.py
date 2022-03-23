# Import
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pandas as pd
import numpy as np


# set the device we will be using to train the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_tensor(file_name, dtype):
    return [dtype(d) for d in np.load(file_name + ".npy", allow_pickle=True)]


def shuffle_dataset(dataset, seed):
    np.random.seed(seed)
    np.random.shuffle(dataset)
    return dataset


def split_dataset(dataset, ratio):
    n = int(ratio * len(dataset))
    dataset_1, dataset_2 = dataset[:n], dataset[n:]
    return dataset_1, dataset_2


# Load preprocessed data
dir_input = "features/"
features = load_tensor(dir_input + "features", torch.FloatTensor)
labels = load_tensor(dir_input + "labels", torch.LongTensor)


# Create a dataset and split it into train/dev/test
dataset = list(zip(features, labels))
dataset = shuffle_dataset(dataset, 1234)
dataset_train, dataset_test = split_dataset(dataset, 0.85)
print(len(dataset_train))
print(len(dataset_test))

# Create simple CNN
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=64,
            kernel_size=(1, 616),
            stride=(1, 1),
            padding=(0, 0),
        )
        self.fc1 = nn.Linear(64, num_classes)

    def forward(self, x):
        x = x.unsqueeze(0)
        x = x.unsqueeze(0)
        x = F.relu(self.conv1(x))
        x = x.view(x.size(0), -1)
        x = self.fc1(x)

        return x


# Hyperparameters
in_channel = 1
num_classes = 2
learning_rate = 0.001
batch_size = 64
num_epochs = 10

# initialize network
model = CNN().to(device)
print(model)


# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)


# Train network
for epoch in range(num_epochs):
    print("epochs:", epoch)
    for i, (x_train, y_train) in enumerate(dataset_train, 1):
        # Get data to cuda if possible
        x_train = x_train.to(device=device)
        y_train = y_train.to(device=device)
        # x_train = x_train.reshape(x_train.shape[0], 1)
        x_train = torch.reshape(x_train, (1, 616)).to(device)
        # forward
        scores = model(x_train)
        loss = criterion(scores, y_train)

        # backward
        optimizer.zero_grad()
        loss.backward()

        # gradient descent or adam strep
        optimizer.step()


# check accuracy on training & test to see how good our model

num_correct = 0
total = len(dataset_test)
print("evaluting trained model ...")
y_pred = []
with torch.no_grad():
    for x_test, y_test in dataset_test:
        x_test = x_test.to(device=device)
        y_test = y_test.to(device=device)
        # x_test = x_test.reshape(x_test.shape[0], 1)
        x_test = torch.reshape(x_test, (1, 616)).to(device)
        scores = model(x_test)
        loss = criterion(scores, y_test)
        _, predictions = scores.max(1)
        num_correct += (predictions == y_test).item()

    print(
        f"Got {num_correct} / {total} with accuracy {float(num_correct)/float(total)*100:.2f}"
    )
