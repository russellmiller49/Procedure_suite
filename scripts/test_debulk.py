import pandas as pd

# Load the data
df = pd.read_csv('data/ml_training/registry_train.csv')

# Filter for the anomaly: Debulking=1 but Rigid=0
anomaly = df[
    (df['tumor_debulking_non_thermal'] == 1) & 
    (df['rigid_bronchoscopy'] == 0)
]

print(f"Found {len(anomaly)} suspicious cases.\n")

# Print the first 200 characters of a few examples to verify context
for i, row in anomaly.head(5).iterrows():
    print(f"--- Case {row.get('encounter_id', 'Unknown')} ---")
    print(row['note_text'][:300].replace('\n', ' '))
    print("\n")