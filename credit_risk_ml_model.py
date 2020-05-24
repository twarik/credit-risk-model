#Load the libraries
import pandas as pd
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
import joblib

import warnings
warnings.filterwarnings('ignore')

#Importing the data
credit_data = pd.read_csv("german_credit_data.csv",index_col=0)
credit_data.head(2)

# check percentage of missing values per column
credit_data.isnull().sum()/len(credit_data)*100

credit_data.info()

class_distribution = credit_data['Risk'].value_counts()/len(credit_data['Risk'])*100
print('Class Distribution')
print(class_distribution)

# Treating Misssing values
# Replace missing values with new unique value (na)
credit_data['Saving accounts'] = credit_data['Saving accounts'].fillna('na')
credit_data['Checking account'] = credit_data['Checking account'].fillna('na')


def transform_data(data):
    '''
    function to transfrom credit risk data
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
    # Risk
    risk = {'bad':0, 'good':1}
    data['Risk'] = data['Risk'].apply(lambda x:risk[x])

    return data

#Data transformation
credit_data = transform_data(credit_data)

# split dataset into dependent and independent variables
X = credit_data.drop('Risk', axis=1).values
y = credit_data["Risk"].values

# Spliting data into train and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state=42)

# logistic regression object
lr = LogisticRegression()

# train the model on train set
lr.fit(X_train, y_train)

predictions = lr.predict(X_test)

print('Logistic regression classifier classification report')
print(classification_report(y_test, predictions).upper())

# XGBoost random forest classifier
xgb = XGBClassifier(n_jobs=-1,nthread=-1)
xgb.fit(X_train, y_train.ravel())

y_pred = xgb.predict(X_test)

print('XGBoost random forest classifier classification report')
print(classification_report(y_test, y_pred).upper())

#Hyper paramter tuning
#perform a grid search over the learning rate, n_estimators, max_depth, min_child_weight, gamma, subsample and colsample_bytree
#Set the Hyper Parameters
param_test1 = {'max_depth':[3,5,6,10],
               'min_child_weight':[3,5,10],
               'gamma':[0.0, 0.1, 0.2, 0.3, 0.4],
               "n_estimators":[3,5,10,25,50,150],
               "learning_rate": [0.001,0.01,0.1],
               'subsample':[i/100.0 for i in range(75,90,5)],
               'colsample_bytree':[i/100.0 for i in range(75,90,5)]}

#Create the XGB Classifier
model_xgb = XGBClassifier(n_jobs=-1,nthread=-1, random_state=42)

grid_search = GridSearchCV(model_xgb, param_grid=param_test1, cv=5, scoring='recall')
# Re-train the final model using the whole data
grid_search.fit(X,y)

print(grid_search.best_score_)
print(grid_search.best_params_)

# Performance evaluation
y_pred = grid_search.predict(X_test)

print("\n")
print('XGBoost classifier classification report (after Hyperparameter tuning)')
print(classification_report(y_test, y_pred).upper())

#Save the retrained model onto the filesystem
joblib.dump(grid_search, 'credit_risk_model.pkl')
print("\n")
print("Retrained Model Saved!")
