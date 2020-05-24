import io
import json
import joblib

def load_model():
     """Load xgboost model."""
     global credit_model
     credit_model = joblib.load("./application/credit_risk_model.pkl")

# Load trained models
load_model()

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
