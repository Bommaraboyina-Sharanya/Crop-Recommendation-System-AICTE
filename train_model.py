import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('dataset/crop_data.csv')

print(f"Dataset shape: {df.shape}")
print(f"\nCrop distribution:\n{df['label'].value_counts()}")

# Features and target
X = df.drop('label', axis=1)
y = df['label']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nTraining set size: {X_train.shape[0]}")
print(f"Test set size: {X_test.shape[0]}")

# Train Random Forest model
print("\nTraining Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# Save the model
os.makedirs('model', exist_ok=True)
with open('model/crop_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("\n✓ Model saved successfully as 'model/crop_model.pkl'")

# Save feature names for later use
with open('model/feature_names.pkl', 'wb') as f:
    pickle.dump(list(X.columns), f)

print("✓ Feature names saved successfully")

# Test prediction example
sample_input = np.array([[90, 42, 43, 20.87, 82.00, 6.50, 202.93]])
sample_prediction = model.predict(sample_input)
print(f"\nSample prediction: {sample_prediction[0]}")
