import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
data = pd.read_csv("Dataset.csv")

# Create encoders
le_interest = LabelEncoder()
le_career = LabelEncoder()

# Encode text columns
data['interest_area'] = le_interest.fit_transform(data['interest_area'])
data['career_label'] = le_career.fit_transform(data['career_label'])

# Split features and target
X = data.drop('career_label', axis=1)
y = data['career_label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)
print("Model Accuracy:", accuracy)

# Save model and encoders
pickle.dump(model, open("career_model.pkl", "wb"))
pickle.dump(le_interest, open("interest_encoder.pkl", "wb"))
pickle.dump(le_career, open("career_encoder.pkl", "wb"))

print("Classes in career_label encoder:")
print(le_career.classes_)