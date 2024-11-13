# utils/data.py
import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_preprocess_data(data_url):
    data = pd.read_csv(data_url)
    data = data.dropna(subset=['Age', 'Fare', 'Pclass', 'Sex', 'Survived'])
    data['Sex'] = data['Sex'].map({'male': 0, 'female': 1})
    X = data[['Pclass', 'Age', 'Fare', 'Sex']]
    y = data['Survived']
    return train_test_split(X, y, test_size=0.2, random_state=42)