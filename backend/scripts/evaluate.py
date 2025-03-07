import os
import sys; sys.path.append('.')
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from datasets.testDataset import getDataset
from models.model import getModel

def evaluate():
    # Define device (GPU if available, else CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Initialize model and move it to the selected device
    model = getModel().to(device)
    backup_model_path = 'models/model_backup_epoch.pth'

    # Load model checkpoint if available
    if os.path.exists(backup_model_path):
        print("Loading model from backup...")
        model.load_state_dict(torch.load(backup_model_path, map_location=device))

    # Load dataset
    dataset = getDataset()

    # Prepare DataLoader
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4, pin_memory=True if device == "cuda" else False)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()


    model.eval()  # Set model to training mode
    total_loss = 0.0
    total = 0
    correct = 0
    
    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)  # Move data to devi ce
        
        outputs = model(images)  # Forward pass
        loss = criterion(outputs, labels)  # Compute loss        
        total_loss += loss.item()
        
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    avg_loss = total_loss / len(dataloader)
    accuracy = 100 * correct / total
    print(f"Test Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
     

if __name__ == '__main__': 
    evaluate()