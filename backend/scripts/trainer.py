import os
import sys; sys.path.append('.')
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from backend.datasets.trainDataset import getDataset
from backend.models.model import getModel
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(markup=True)]
)

# global vairables 
train_dic = 'backend/data/cleaned'
train_epoch = 10

def train():
    # Define device (GPU if available, else CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    # Initialize model and move it to the selected device
    model = getModel().to(device)
    backup_model_path = 'backend/outputs/model_backup_epoch.pth'

    # Load model checkpoint if available
    if os.path.exists(backup_model_path):
        logging.info("Loading model from backup...")
        model.load_state_dict(torch.load(backup_model_path, map_location=device))

    # Load dataset
    dataset = getDataset(train_dic)

    # Prepare DataLoader
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4, pin_memory=True if device == "cuda" else False)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # Training parameters
    epochs = train_epoch

    # Training loop
    try:
        for epoch in range(1, epochs + 1):
            model.train()  # Set model to training mode
            running_loss = 0.0
            
            for images, labels in dataloader:
                images, labels = images.to(device), labels.to(device)  # Move data to device
                
                optimizer.zero_grad()  # Clear previous gradients
                output = model(images)  # Forward pass
                loss = criterion(output, labels)  # Compute loss
                loss.backward()  # Backward pass
                optimizer.step()  # Update model weights
                
                running_loss += loss.item()
            
            # Print and save model every 2 epochs
            if epoch % 2 == 0:
                avg_loss = running_loss / len(dataloader)
                logging.info(f'Epoch [{epoch}/{epochs}], Loss: {avg_loss:.4f}')
                torch.save(model.state_dict(), backup_model_path)

    except KeyboardInterrupt:
        logging.info("Training interrupted. Saving model checkpoint...")
        torch.save(model.state_dict(), 'backend/outputs/model_backup.pth')

if __name__ == '__main__': 
    train()