import io
import json
import joblib
from PIL import Image
import torch
from torchvision import models, transforms

resnet_class_index = json.load(open('./application/resnet_class_index.json'))

def load_model():
     """Load Pytorch-ResNet50 and sklearn model."""
     global model
     global credit_model
     global titanic_model
     # Load Pytorch pretrained model with imageNet weights
     model = models.resnet50(pretrained=True)
     model.eval()
     # load sklearn  model
     credit_model = joblib.load("./application/credit_risk_model.pkl")

# Load trained models
load_model()

def image_model(image_bytes):
    '''
    Function to pre-process the input image to a format similar to training data and
    then make predictions on the image
    '''
    # define the various image transformations we have to make
    transform = transforms.Compose([transforms.Resize(255),
                                    transforms.CenterCrop(224),
                                    transforms.ToTensor(),
                                    transforms.Normalize([0.485, 0.456, 0.406],
                                                        [0.229, 0.224, 0.225])])

    # Open and identify the uploaded/given image file.
    image = Image.open(io.BytesIO(image_bytes))
    # Pre-process the uploaded image
    tensor = transform(image).unsqueeze(0)

    # Make predictions
    outputs = model.forward(tensor)
    _, indices = torch.sort(outputs, descending=True)
    confidence = torch.nn.functional.softmax(outputs, dim=1)[0]

    # Return the top 3 pedictions ('class label, probability')
    result = [ (resnet_class_index[str(idx.item())][1], confidence[idx].item()) for idx in indices[0][:5] ]
    return result

def transform_data(data):
    '''
    function to transfrom and prepare credit risk data
    '''
    # Age categorization (convert the ages into categorical representation)
    data.loc[ data['Age'] <= 17, 'Age'] = 0 # Young
    data.loc[(data['Age'] > 17) & (data['Age'] <= 25), 'Age'] = 1 # Young Adults
    data.loc[(data['Age'] > 25) & (data['Age'] <= 35), 'Age'] = 2 # Young Adults 1
    data.loc[(data['Age'] > 35) & (data['Age'] <= 50), 'Age'] = 3 # Middle-aged Adults
    data.loc[(data['Age'] > 50) & (data['Age'] <= 65), 'Age'] = 4 # Middle-aged Adults 2
    data.loc[(data['Age'] > 65), 'Age'] = 5 # Senior citizens
    data.head(2)
    # convert categorical data into numeric represantation
    # sex
    gender = {'male' :1, 'female': 2 }
    data['Sex'] = data['Sex'].apply(lambda x:gender[x])
    # Housing
    house = {'own' :1, 'free': 2, 'rent': 3}
    data['Housing'] = data['Housing'].apply(lambda x:house[x])
    # Saving accounts
    savings = {'na': 0,'little' :1, 'moderate': 2, 'rich': 3, 'quite rich': 4}
    data['Saving accounts'] = data['Saving accounts'].apply(lambda x:savings[x])
    # Checking account
    checking = {'na': 0,'little' :1, 'moderate': 2, 'rich': 3}
    data['Checking account'] = data['Checking account'].apply(lambda x:checking[x])
    # Purpose
    purpose = {'radio/TV':1, 'education':2, 'furniture/equipment':3, 'car':4, 'business':5,
               'domestic appliances':6, 'repairs':7, 'vacation/others':8}
    data['Purpose'] = data['Purpose'].apply(lambda x:purpose[x])

    return data
