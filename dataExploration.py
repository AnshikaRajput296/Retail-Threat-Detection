import matplotlib.pyplot as plt
import pandas as pd
from functools import reduce
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import seaborn as sns

device_df=pd.read_csv('device.csv')
#http file did not have column headers so i added them
http_headers = ['id', 'date', 'time', 'user', 'pc', 'url', 'content', 'bytes_sent', 'bytes_received']
http_df = pd.read_csv('http.csv', header=None, names=http_headers)
logon_df=pd.read_csv('logon.csv')

#counting number of activities done by a particular user on the specific date
logon_agg = logon_df.groupby(['user', 'date']).agg({
    'activity': 'count'     
}).reset_index().rename(columns={
    'activity': 'logon_count'
})

#count the number of sites visited,bytes recieved/send by a user on the date
http_agg = http_df.groupby(['user', 'date']).agg({
    'url': 'count',         
    'bytes_sent': 'sum',  
    'bytes_received': 'sum' 
}).reset_index().rename(columns={
    'url': 'http_requests',
    'bytes_sent': 'http_bytes_sent',
    'bytes_received': 'http_bytes_received'
})

#counting number of activities done by a particular user on the specific date
device_agg = device_df.groupby(['user', 'date']).agg({
    'activity': 'count'
}).reset_index().rename(columns={'activity': 'device_activity_count'})


#merged all the data in a single dataframe:merged_df
dfs = [logon_agg, http_agg, device_agg]
merged_df = reduce(lambda left, right: pd.merge(left, right, on=['user', 'date'], how='outer'), dfs)
merged_df.fillna(0, inplace=True)

#converted date object to year,mont,day,weekday,houe,minute,is_working_day
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df['year'] = merged_df['date'].dt.year
merged_df['month'] = merged_df['date'].dt.month
merged_df['day'] = merged_df['date'].dt.day
merged_df['weekday'] = merged_df['date'].dt.weekday  # Monday=0, Sunday=6
merged_df['hour'] = merged_df['date'].dt.hour
merged_df['minute'] = merged_df['date'].dt.minute
merged_df['is_working_day'] = merged_df['weekday'].apply(lambda x: 1 if x < 5 else 0)

#User-Specific Behavioral Patterns: to check if the user deviated from his usual pattern
user_baseline = merged_df.groupby('user').agg({
    'logon_count': ['mean', 'std'],
    'http_requests': ['mean', 'std'],
    'device_activity_count': ['mean', 'std']
})
user_baseline.columns = ['_'.join(col) for col in user_baseline.columns]
user_baseline.reset_index(inplace=True)
merged_df = merged_df.merge(user_baseline, on='user', how='left')
merged_df['logon_spike'] = (merged_df['logon_count'] - merged_df['logon_count_mean']) / merged_df['logon_count_std']
merged_df['http_spike'] = (merged_df['http_requests'] - merged_df['http_requests_mean']) / merged_df['http_requests_std']
merged_df['device_spike'] = (merged_df['device_activity_count'] - merged_df['device_activity_count_mean']) / merged_df['device_activity_count_std']

#Detect unusual usage emphasis (if there unusual high activity by a user)
merged_df['device_http_ratio'] = merged_df['device_activity_count'] / (merged_df['http_requests'] + 1)
merged_df['logon_http_ratio'] = merged_df['logon_count'] / (merged_df['http_requests'] + 1)

#Check if the person has unusual activity after work hours
merged_df['week_of_month'] = merged_df['day'].apply(lambda d: (d - 1) // 7 + 1)
merged_df['is_off_hours'] = merged_df['hour'].apply(lambda h: 1 if (h < 7 or h > 19) else 0)

#Detect change over time for a user
merged_df = merged_df.sort_values(['user', 'date'])
merged_df['logon_rolling_3'] = merged_df.groupby('user')['logon_count'].transform(lambda x: x.rolling(3, min_periods=1).mean())
merged_df['logon_delta'] = merged_df['logon_count'] - merged_df['logon_rolling_3']

#Insider behavior might include skipping typical actions
merged_df['http_missing'] = (merged_df['http_requests'] == 0).astype(int)
merged_df['device_missing'] = (merged_df['device_activity_count'] == 0).astype(int)
merged_df['logon_missing'] = (merged_df['logon_count'] == 0).astype(int)


features_to_keep = [
    'logon_count',
    'http_requests',
    'http_bytes_sent',
    'http_bytes_received',
    'device_activity_count',
    
    'logon_spike',
    'http_spike',
    'device_spike',
    
    'device_http_ratio',
    'logon_http_ratio',
    
    'hour',
    'weekday',
    'is_working_day',
    'is_off_hours',
    
    'logon_rolling_3',
    'logon_delta'
]
#Final training data
X = merged_df[features_to_keep].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,  # 2% of data assumed anomalous
    max_samples='auto',
    max_features=1.0,
    bootstrap=False,
    n_jobs=-1,
    random_state=42
)

model.fit(X_scaled)
merged_df['anomaly'] = model.predict(X_scaled)

merged_df['anomaly_score'] = model.decision_function(X_scaled)
merged_df['risk_score'] = -merged_df['anomaly_score']
low_thresh = merged_df['risk_score'].quantile(0.75)
high_thresh = merged_df['risk_score'].quantile(0.95)

def classify_risk(score):
    if score < low_thresh:
        return 'Low'
    elif score < high_thresh:
        return 'Medium'
    else:
        return 'High'

merged_df['risk_level'] = merged_df['risk_score'].apply(classify_risk)
print("Anomaly counts:")
print(merged_df['anomaly'].value_counts())
print("\nRisk Level Distribution:")
print(merged_df['risk_level'].value_counts())
top_risks = merged_df[merged_df['risk_level'] == 'High'].sort_values(by='risk_score', ascending=False)
print("\nTop 5 High Risk Records:")
print(top_risks[['user', 'date', 'risk_score', 'risk_level']].head())

plt.figure(figsize=(6,4))
sns.countplot(data=merged_df, x='risk_level', order=['Low', 'Medium', 'High'], palette='coolwarm')
plt.title('Risk Level Distribution')
plt.show()
