import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from alibi.explainers import AnchorTabular
from alibi.datasets import fetch_adult

adult = fetch_adult()
adult.keys()
data = adult.data
target = adult.target
feature_names = adult.feature_names
category_map = adult.category_map

print(feature_names)
print(category_map)