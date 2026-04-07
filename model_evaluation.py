import pandas as pd
import matplotlib.pyplot as plt
import pickle

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# Load dataset
data = pd.read_csv("Dataset.csv")   # change this to career_data.csv if needed

# Encode text columns
le_interest = LabelEncoder()
le_career = LabelEncoder()

data['interest_area'] = le_interest.fit_transform(data['interest_area'])
data['career_label'] = le_career.fit_transform(data['career_label'])

# Split features and target
X = data.drop('career_label', axis=1)
y = data['career_label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Define models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42)
}

accuracies = {}
best_model = None
best_accuracy = 0
best_model_name = ""

# Train and evaluate models
for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    accuracies[name] = accuracy

    print(f"{name} Accuracy: {accuracy:.2f}")

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model
        best_model_name = name

print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.2f}")

# 1. Accuracy Comparison Graph
plt.figure(figsize=(8, 5))
plt.bar(accuracies.keys(), accuracies.values())
plt.title("Model Accuracy Comparison")
plt.xlabel("Models")
plt.ylabel("Accuracy")
plt.ylim(0, 1.1)
plt.tight_layout()
plt.savefig("accuracy_comparison.png")
plt.close()

# 2. Confusion Matrix
best_predictions = best_model.predict(X_test)

all_labels = list(range(len(le_career.classes_)))
cm = confusion_matrix(y_test, best_predictions, labels=all_labels)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=le_career.classes_
)

fig, ax = plt.subplots(figsize=(10, 7))
disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
plt.title(f"Confusion Matrix - {best_model_name}")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()

# 3. Feature Importance Graph
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

feature_importance = rf_model.feature_importances_
feature_names = X.columns

plt.figure(figsize=(10, 6))
plt.barh(feature_names, feature_importance)
plt.title("Feature Importance - Random Forest")
plt.xlabel("Importance Score")
plt.ylabel("Features")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.close()

# Save best model
pickle.dump(best_model, open("best_model.pkl", "wb"))

print("\nAll graphs saved successfully:")
print("1. accuracy_comparison.png")
print("2. confusion_matrix.png")
print("3. feature_importance.png")