import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

# Load dataset
df = pd.read_csv('bus_dataset.csv')

# One-hot encode
df = pd.get_dummies(df)

# Split features and target
X = df.drop('Range_per_Charge', axis=1)
y = df['Range_per_Charge']


# Train model
model = RandomForestRegressor()
model.fit(X, y)

# Save model and feature columns
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(X.columns.tolist(), open('columns.pkl', 'wb'))
