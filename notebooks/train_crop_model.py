import os
import joblib
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

def train_and_evaluate():
    # 1. Dataset Path Setup
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'data', 'Crop_recommendation.csv')
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    print("==================================================")
    print("      CROP RECOMMENDATION ML TRAINING PIPELINE    ")
    print("==================================================")
    print(f"Dataset Path: {dataset_path}")
    print(f"Dataset Exists: {os.path.exists(dataset_path)}")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}. Training cannot proceed without data.")

    # 2. Load Dataset
    df = pd.read_csv(dataset_path)

    # 3. Exploratory Data Analysis & Quality Inspection
    rows, cols = df.shape
    missing_vals = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    unique_crops = df['label'].nunique() if 'label' in df.columns else 0
    crop_counts = df['label'].value_counts().to_dict() if 'label' in df.columns else {}

    print(f"\n--- DATASET INSPECTION ---")
    print(f"Total Rows: {rows}")
    print(f"Total Columns: {cols}")
    print(f"Column Names: {list(df.columns)}")
    print(f"Missing Values Count: {missing_vals}")
    print(f"Duplicate Rows Count: {duplicate_rows}")
    print(f"Unique Crop Classes ({unique_crops}): {list(crop_counts.keys())}")

    # 4. Feature & Target Validation
    expected_features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    target_col = "label"

    for feat in expected_features:
        if feat not in df.columns:
            raise KeyError(f"Required feature '{feat}' is missing from the dataset.")

    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' is missing from the dataset.")

    # 5. Cleaning Dataset (deduplication if needed)
    if duplicate_rows > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        print(f"Cleaned dataset: Removed {duplicate_rows} duplicate rows. New row count: {len(df)}")

    X = df[expected_features]
    y = df[target_col]

    # 6. Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain set size: {len(X_train)} samples | Test set size: {len(X_test)} samples")

    # 7. Model Training & Comparison
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "SVM (Scaled)": Pipeline([
            ('scaler', StandardScaler()),
            ('svm', SVC(kernel='rbf', C=1.0, probability=True, random_state=42))
        ])
    }

    results = {}
    print("\n--- MODEL COMPARISON RESULTS ---")

    best_model_name = None
    best_f1 = 0.0
    best_model_obj = None

    for name, model in models.items():
        # Train model
        model.fit(X_train, y_train)

        # Predictions
        train_preds = model.predict(X_train)
        test_preds = model.predict(X_test)

        # Metrics
        train_acc = accuracy_score(y_train, train_preds)
        test_acc = accuracy_score(y_test, test_preds)
        precision = precision_score(y_test, test_preds, average='weighted')
        recall = recall_score(y_test, test_preds, average='weighted')
        f1 = f1_score(y_test, test_preds, average='weighted')

        overfitting_gap = round((train_acc - test_acc) * 100, 2)

        results[name] = {
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "overfitting_gap_pct": overfitting_gap
        }

        print(f"\nModel: {name}")
        print(f"  Train Accuracy : {train_acc * 100:.2f}%")
        print(f"  Test Accuracy  : {test_acc * 100:.2f}%")
        print(f"  Precision      : {precision:.4f}")
        print(f"  Recall         : {recall:.4f}")
        print(f"  F1-Score       : {f1:.4f}")
        print(f"  Train-Test Gap : {overfitting_gap}%")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model

    print(f"\n>>> SELECTED BEST MODEL: {best_model_name} (Test F1-Score: {best_f1:.4f}) <<<")

    # 8. Detailed Evaluation for Selected Model
    selected_preds = best_model_obj.predict(X_test)
    report = classification_report(y_test, selected_preds)
    cm = confusion_matrix(y_test, selected_preds)

    print("\n--- CLASSIFICATION REPORT (BEST MODEL) ---")
    print(report)

    # 9. Save Selected Trained Model & Official Feature Order
    saved_model_path = os.path.join(models_dir, 'crop_model.pkl')
    
    # Store required feature order on model object for runtime inference safety
    if hasattr(best_model_obj, 'feature_names_in_'):
        pass
    else:
        best_model_obj.feature_names_in_ = np.array(expected_features, dtype=object)

    joblib.dump(best_model_obj, saved_model_path)
    print(f"\nSaved trained model to: {saved_model_path}")

    # 10. Sample Test Predictions
    print("\n--- TESTING SAVED MODEL WITH DIVERSE SAMPLE INPUTS ---")
    loaded_model = joblib.load(saved_model_path)

    sample_cases = [
        {"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9, "expected": "rice"},
        {"N": 118, "P": 45, "K": 20, "temperature": 25.0, "humidity": 60.0, "ph": 6.9, "rainfall": 80.0, "expected": "maize"},
        {"N": 40, "P": 60, "K": 80, "temperature": 17.0, "humidity": 16.0, "ph": 7.5, "rainfall": 75.0, "expected": "chickpea"},
        {"N": 100, "P": 10, "K": 50, "temperature": 28.0, "humidity": 85.0, "ph": 6.3, "rainfall": 50.0, "expected": "watermelon"},
        {"N": 100, "P": 28, "K": 30, "temperature": 26.5, "humidity": 98.0, "ph": 6.8, "rainfall": 150.0, "expected": "coffee"}
    ]

    sample_predictions = []
    for idx, case in enumerate(sample_cases, 1):
        expected_label = case.pop("expected")
        input_df = pd.DataFrame([case], columns=expected_features)
        pred_label = loaded_model.predict(input_df)[0]
        
        prob_str = ""
        if hasattr(loaded_model, 'predict_proba'):
            probas = loaded_model.predict_proba(input_df)[0]
            classes = loaded_model.classes_ if hasattr(loaded_model, 'classes_') else loaded_model.named_steps['svm'].classes_
            top_prob = max(probas) * 100
            prob_str = f" (Confidence: {top_prob:.1f}%)"

        res = {
            "case": idx,
            "inputs": case,
            "expected_reference": expected_label,
            "predicted_crop": pred_label,
            "confidence_pct": round(top_prob, 2) if hasattr(loaded_model, 'predict_proba') else None
        }
        sample_predictions.append(res)
        print(f"Sample {idx}: Inputs={case}")
        print(f"  --> Predicted: '{pred_label}'{prob_str} | Expected: '{expected_label}'\n")

    # 11. Save Evaluation Summary Output
    eval_output_path = os.path.join(base_dir, 'data', 'crop_model_evaluation.json')
    eval_data = {
        "dataset_rows": rows,
        "dataset_cols": cols,
        "num_classes": unique_crops,
        "features": expected_features,
        "models_evaluated": results,
        "best_model": best_model_name,
        "test_accuracy": round(accuracy_score(y_test, selected_preds), 4),
        "sample_predictions": sample_predictions
    }

    with open(eval_output_path, 'w') as f:
        json.dump(eval_data, f, indent=2)

    print(f"Saved evaluation metrics log to: {eval_output_path}")

if __name__ == '__main__':
    train_and_evaluate()
