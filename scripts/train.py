import torch
import torch.optim as optim 
from utils.datasets import getDataset
from models.model import getModel

model = getModel()
dataset = getDataset()
data