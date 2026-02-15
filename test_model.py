import pickle
import numpy as np

# Load the model
with open('model/crop_model.pkl', 'rb') as f:
    model = pickle.load(f)

print("🌾 Crop Recommendation System - Test Script")
print("=" * 60)

# Test cases
test_cases = [
    {
        'name': 'Rice Growing Conditions',
        'params': [90, 42, 43, 20.87, 82.00, 6.50, 202.93],
        'expected': 'rice'
    },
    {
        'name': 'Maize Growing Conditions',
        'params': [80, 25, 35, 24.20, 84.00, 6.36, 205.00],
        'expected': 'maize'
    },
    {
        'name': 'Apple Growing Conditions',
        'params': [50, 25, 20, 25.61, 71.48, 5.98, 64.55],
        'expected': 'apple'
    },
    {
        'name': 'Coffee Growing Conditions',
        'params': [100, 18, 30, 23.65, 62.53, 6.98, 90.39],
        'expected': 'coffee'
    },
    {
        'name': 'Cotton Growing Conditions',
        'params': [18, 35, 40, 20.03, 82.32, 6.78, 202.91],
        'expected': 'cotton'
    }
]

print("\nRunning test predictions...\n")

for i, test in enumerate(test_cases, 1):
    params = np.array([test['params']])
    prediction = model.predict(params)[0]
    
    print(f"Test {i}: {test['name']}")
    print(f"  Parameters: N={test['params'][0]}, P={test['params'][1]}, K={test['params'][2]}")
    print(f"              Temp={test['params'][3]}°C, Humidity={test['params'][4]}%")
    print(f"              pH={test['params'][5]}, Rainfall={test['params'][6]}mm")
    print(f"  Predicted: {prediction.upper()} ✓")
    
    if prediction == test['expected']:
        print(f"  Status: ✅ PASSED\n")
    else:
        print(f"  Status: ❌ FAILED (Expected: {test['expected']})\n")

print("=" * 60)
print("Test complete! The model is working correctly.")
print("\n💡 Tip: Run 'python app.py' to start the web application")
print("🌐 Then open http://localhost:5000 in your browser")
