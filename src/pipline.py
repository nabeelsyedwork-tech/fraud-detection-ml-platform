import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load dataset
df = pd.read_csv('creditcard.csv')
X = df.drop(['Class'], axis=1)
y = df['Class']

# Split data
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Compute class weight
weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
model = XGBClassifier(
    max_depth=5,
    learning_rate=0.2942758, 
    n_estimators=110,
    scale_pos_weight=288.01128,
    eval_metric="mlogloss"
    )

model.fit(x_train,y_train)

joblib.dump(model,filename='model.pkl')