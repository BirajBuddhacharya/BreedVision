import torch 
import torch.nn as nn 
from torchvision.models import resnet50

class BreedClassifier(nn.Module): 
    def __init__(self): 
        super(BreedClassifier, self).__init__()
        self.model = resnet50(pretrained = True)
        
        # freezing all layers except last fc layer
        for param in self.model.parameters(): 
            param.requires_grad = False
        
        in_features = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, 200)

    def forward(self, x): 
        return self.model(x)

def getModel(): 
    # selecting device 
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # making model instance and moving it to device
    model = BreedClassifier().to(device)
    
    return model
    
if __name__ == '__main__':
    model = getModel()
    print(model)