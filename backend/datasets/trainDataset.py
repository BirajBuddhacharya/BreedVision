from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms

def getDataset(): 
    # formating image and augmenting data
    transform = transforms.Compose([
        transforms.Resize((256, 256)),  # Resize to slightly larger than final size
        transforms.RandomApply([
            transforms.RandomResizedCrop((224, 224), scale=(0.8, 1.0), ratio=(0.9, 1.1))
        ], p=0.5),
        transforms.CenterCrop(224),  # Ensure 224x224 when RandomResizedCrop is not applied
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomApply([transforms.RandomRotation(15)], p=0.5),
        transforms.RandomApply([
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1)
        ], p=0.5),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet means
            std=[0.229, 0.224, 0.225]    # ImageNet stds
        )
    ])
    
    dataset = ImageFolder('data/train', transform=transform)
    
    return dataset

if __name__ == '__main__': 
    import matplotlib.pyplot as plt
    dataset = getDataset()
    
    for img, label in dataset: 
        plt.imshow(img.permute(1, 2, 0).numpy())
        plt.axis("off")
        plt.show()