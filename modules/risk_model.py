from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

MODEL_PATH = Path('data/risk_model.pkl')


def create_sample_training_data(n=500, random_state=42):
    rng = np.random.default_rng(random_state)
    data = pd.DataFrame({
        'total_lines': rng.integers(10, 1000, n),
        'issue_count': rng.integers(0, 50, n),
        'functions': rng.integers(0, 150, n),
        'classes': rng.integers(0, 40, n),
        'imports': rng.integers(0, 100, n),
    })
    score = (
        data['issue_count'] * 3
        + data['total_lines'] / 120
        + data['functions'] / 10
        + data['classes'] / 5
        + data['imports'] / 15
    )
    data['risk_label'] = np.where(score > 35, 2, np.where(score > 15, 1, 0))
    return data


def train_model():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = create_sample_training_data()
    X = df[['total_lines', 'issue_count', 'functions', 'classes', 'imports']]
    y = df['risk_label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, preds),
        'confusion_matrix': confusion_matrix(y_test, preds, labels=[0, 1, 2]).tolist(),
        'classification_report': classification_report(y_test, preds, output_dict=True)
    }
    joblib.dump(model, MODEL_PATH)
    return model, metrics


def load_or_train_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH), None
    return train_model()


def predict_risk(metrics: dict, issue_count: int):
    model, _ = load_or_train_model()
    X = pd.DataFrame([{
        'total_lines': metrics.get('total_lines', 0),
        'issue_count': issue_count,
        'functions': metrics.get('functions', 0),
        'classes': metrics.get('classes', 0),
        'imports': metrics.get('imports', 0),
    }])
    label = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]
    risk_map = {0: 'Low', 1: 'Medium', 2: 'High'}
    risk_score = round(float(probabilities[label] * 100), 2)
    return risk_map[label], risk_score, probabilities.tolist()
