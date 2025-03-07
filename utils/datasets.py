from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms

def getDataset(): 
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    dataset = ImageFolder('data/train', transform=transform)
    
    return dataset

if __name__ == '__main__': 
    import matplotlib.pyplot as plt
    dataset = getDataset()
    
    for img, label in dataset: 
        plt.imshow(img.permute(1, 2, 0).numpy())
        break
    plt.show()