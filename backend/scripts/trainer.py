import os
import sys; sys.path.append('.')
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from backend.datasets.trainDataset import getDataset
from backend.models.model import getModel
from rich.logging import RichHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)

# Define number of devices dynamically
WORLD_SIZE = 2 
MASTER_ADDR = "192.168.1.99"  
MASTER_PORT = "12355"

# Global variables
train_dic = 'backend/data/cleaned'
train_epoch = 10
backup_model_path = 'backend/outputs/model_backup_epoch.pth'

def setup(rank, world_size):
    """Initialize distributed processing"""
    os.environ['MASTER_ADDR'] = MASTER_ADDR
    os.environ['MASTER_PORT'] = MASTER_PORT

    backend = "nccl" if torch.cuda.is_available() else "gloo"
    dist.init_process_group(backend=backend, rank=rank, world_size=world_size)
    if backend == "nccl":
        torch.cuda.set_device(rank)

def cleanup():
    """Cleanup distributed training"""
    dist.destroy_process_group()

def train(rank, world_size):
    """Distributed training function"""
    setup(rank, world_size)
    device = torch.device(f'cuda:{rank}' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Rank {rank} using device: {device}")

    # Load model
    model = getModel().to(device)
    model = DDP(model, device_ids=[rank] if device.type == "cuda" else None)

    # Load dataset
    dataset = getDataset(train_dic)
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4, sampler=sampler)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # Load checkpoint if available
    if os.path.exists(backup_model_path):
        logging.info(f"Rank {rank} loading model from backup...")
        model.load_state_dict(torch.load(backup_model_path, map_location=device))

    # Training loop
    try:
        for epoch in range(1, train_epoch + 1):
            model.train()
            sampler.set_epoch(epoch)  # Ensures proper shuffling across nodes
            running_loss = 0.0
            
            for images, labels in dataloader:
                images, labels = images.to(device), labels.to(device)

                optimizer.zero_grad()
                output = model(images)
                loss = criterion(output, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
            
            # Print loss and save model every 2 epochs
            if rank == 0 and epoch % 2 == 0:
                avg_loss = running_loss / len(dataloader)
                logging.info(f'[Epoch {epoch}/{train_epoch}] Loss: {avg_loss:.4f}')
                torch.save(model.state_dict(), backup_model_path)

    except KeyboardInterrupt:
        logging.info(f"Rank {rank} training interrupted. Saving checkpoint...")
        torch.save(model.state_dict(), f'backend/outputs/model_backup_rank{rank}.pth')

    cleanup()

if __name__ == "__main__":
    mp.spawn(train, args=(WORLD_SIZE,), nprocs=WORLD_SIZE)
