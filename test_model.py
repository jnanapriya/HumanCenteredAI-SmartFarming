#!/usr/bin/env python3
"""
Complete diagnostic test for crop_model.pkl
Tests model predictions with 10+ realistic input combinations
"""
import joblib
import os
import numpy as np
import pandas as pd

print('='*90)
print('COMPREHENSIVE CROP MODEL DIAGNOSTIC TEST')
print('='*90)

# Load model
model_path = 'models/crop_model.pkl'
print(f'\n1. LOADING MODEL')
print(f'   Path: {model_path}')
print(f'   Exists: {os.path.exists(model_path)}')
print(f'   Size: {os.path.getsize(model_path):,} bytes')

model = joblib.load(model_path)

# Verify model attributes
print(f'\n2. MODEL ATTRIBUTES')
print(f'   Type: {type(model).__name__}')
print(f'   Has predict: {hasattr(model, "predict")}')
print(f'   Has predict_proba: {hasattr(model, "predict_proba")}')
print(f'   Has feature_names_in_: {hasattr(model, "feature_names_in_")}')
print(f'   Has classes_: {hasattr(model, "classes_")}')

# Extract feature order
if hasattr(model, 'feature_names_in_'):
    feature_names = list(model.feature_names_in_)
    print(f'\n3. EXACT FEATURE ORDER FROM MODEL')
    print(f'   Feature count: {len(feature_names)}')
    for i, feat in enumerate(feature_names):
        print(f'   Position {i}: "{feat}"')
else:
    print(f'\n3. WARNING: Model lacks feature_names_in_ attribute')
    feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    print(f'   Using assumed order: {feature_names}')

# Extract classes
if hasattr(model, 'classes_'):
    classes = list(model.classes_)
    print(f'\n4. CROP CLASSES')
    print(f'   Total: {len(classes)}')
    print(f'   Classes: {classes}')
else:
    print(f'\n4. WARNING: Model lacks classes_ attribute')

# Feature importances
if hasattr(model, 'feature_importances_'):
    print(f'\n5. FEATURE IMPORTANCES')
    importances = model.feature_importances_
    for feat, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
        print(f'   {feat:15}: {imp:.4f} ({imp*100:.1f}%)')

print('\n' + '='*90)
print('TESTING 12 REALISTIC INPUT COMBINATIONS')
print('='*90)

# 12 realistic test cases covering different crops
test_cases = [
    # [N, P, K, temp, hum, ph, rain], 'label', 'expected_crop'
    ([90, 42, 43, 20.8, 82.0, 6.5, 202.9], 'Rice (form default)', 'rice'),
    ([80, 40, 40, 23, 80, 6.5, 200], 'Rice typical', 'rice'),
    ([80, 48, 40, 23.7, 82.3, 6.4, 236], 'Rice (dataset mean)', 'rice'),
    
    ([80, 40, 20, 24, 65, 6.5, 90], 'Maize typical', 'maize'),
    ([118, 45, 20, 25.0, 60.0, 6.9, 80.0], 'Maize (eval sample)', 'maize'),
    
    ([100, 28, 30, 26, 58, 6.8, 150], 'Coffee typical', 'coffee'),
    ([101, 29, 30, 25.5, 59, 6.8, 158], 'Coffee (dataset mean)', 'coffee'),
    
    ([20, 17, 31, 27, 95, 6.0, 180], 'Coconut typical', 'coconut'),
    ([22, 17, 31, 27.4, 94.8, 6.0, 176], 'Coconut (dataset mean)', 'coconut'),
    
    ([40, 60, 80, 17, 16, 7.5, 75], 'Chickpea typical', 'chickpea'),
    ([100, 10, 50, 28, 85, 6.3, 50], 'Watermelon typical', 'watermelon'),
    ([50, 25, 25, 22, 70, 6.5, 100], 'Mixed moderate values', None),
]

results = []

for i, (inputs, label, expected) in enumerate(test_cases, 1):
    print(f'\n{"─"*90}')
    print(f'Test Case {i:2d}: {label}')
    print(f'{"─"*90}')
    
    # Create DataFrame with exact feature order
    df = pd.DataFrame([inputs], columns=feature_names)
    
    print(f'Input values:')
    print(f'  N={inputs[0]:6.1f}, P={inputs[1]:6.1f}, K={inputs[2]:6.1f}')
    print(f'  Temperature={inputs[3]:6.1f}°C, Humidity={inputs[4]:6.1f}%')
    print(f'  pH={inputs[5]:6.1f}, Rainfall={inputs[6]:6.1f}mm')
    
    # Predict
    pred = model.predict(df)[0]
    
    print(f'\nPredicted crop: {pred}')
    
    # Get probabilities if available
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(df)[0]
        max_prob = max(proba) * 100
        
        # Get top 3
        sorted_idx = np.argsort(proba)[::-1][:3]
        top_3 = [(model.classes_[idx], proba[idx]*100) for idx in sorted_idx]
        
        print(f'Confidence: {max_prob:.1f}%')
        print(f'\nTop 3 predictions:')
        for rank, (crop, prob) in enumerate(top_3, 1):
            print(f'  {rank}. {crop:15} : {prob:5.1f}%')
        
        # Check if expected
        if expected:
            match = pred.lower() == expected.lower()
            status = '✓ CORRECT' if match else f'✗ EXPECTED {expected}'
            print(f'\nResult: {status}')
        
        results.append({
            'label': label,
            'expected': expected,
            'predicted': pred,
            'confidence': max_prob,
            'top_3': top_3,
            'match': pred.lower() == expected.lower() if expected else None
        })
    else:
        print('(probability not available)')
        results.append({
            'label': label,
            'expected': expected,
            'predicted': pred,
            'confidence': None,
            'top_3': None,
            'match': pred.lower() == expected.lower() if expected else None
        })

# Summary statistics
print(f'\n{"="*90}')
print('SUMMARY STATISTICS')
print(f'{"="*90}')

print(f'\nTotal test cases: {len(results)}')
predictions = [r['predicted'] for r in results]
print(f'Unique predictions: {len(set(predictions))}')

# Count each crop
from collections import Counter
pred_counts = Counter(predictions)
print(f'\nPrediction distribution:')
for crop, count in pred_counts.most_common():
    pct = count/len(predictions)*100
    print(f'  {crop:15} : {count:2d} ({pct:5.1f}%)')

# Coffee analysis
coffee_count = predictions.count('coffee')
print(f'\nCoffee predictions: {coffee_count}/{len(results)} ({coffee_count/len(results)*100:.1f}%)')

# Check if coffee appears in top 3
coffee_in_top3 = 0
for r in results:
    if r['top_3']:
        if any(crop.lower() == 'coffee' for crop, _ in r['top_3']):
            coffee_in_top3 += 1
print(f'Coffee in top 3: {coffee_in_top3}/{len(results)} ({coffee_in_top3/len(results)*100:.1f}%)')

# Accuracy on known crops
known_results = [r for r in results if r['expected'] is not None]
if known_results:
    correct = sum(1 for r in known_results if r['match'])
    accuracy = correct / len(known_results) * 100
    print(f'\nAccuracy on known crops: {correct}/{len(known_results)} ({accuracy:.1f}%)')

# Low confidence predictions
low_conf = [r for r in results if r['confidence'] and r['confidence'] < 50]
if low_conf:
    print(f'\nLow confidence predictions (<50%):')
    for r in low_conf:
        print(f'  {r["label"]:30} : {r["predicted"]:15} ({r["confidence"]:.1f}%)')

print(f'\n{"="*90}')
print('DIAGNOSTIC COMPLETE')
print(f'{"="*90}')

# Final assessment
print(f'\nASSESSMENT:')
if len(set(predictions)) >= 5:
    print(f'  ✓ Model produces diverse predictions ({len(set(predictions))} unique crops)')
else:
    print(f'  ✗ Model produces limited diversity ({len(set(predictions))} unique crops)')

if coffee_count <= len(results) * 0.3:
    print(f'  ✓ No coffee bias detected ({coffee_count}/{len(results)} cases)')
else:
    print(f'  ⚠ Coffee appears frequently ({coffee_count}/{len(results)} cases)')

if known_results and accuracy >= 80:
    print(f'  ✓ High accuracy on known crops ({accuracy:.1f}%)')
elif known_results:
    print(f'  ⚠ Low accuracy on known crops ({accuracy:.1f}%)')

print()
