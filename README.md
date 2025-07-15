# 🔐 Retail Insider Threat Detection 🛒🧠  
**Scalable Risk Analytics Dashboard**

Welcome to the **Retail Insider Threat Detection System**,  interactive dashboard for detecting and analyzing potential insider threats in a retail organization. This project leverages real-time user behavior data, anomaly detection, and risk scoring to identify malicious activities using a visual, enterprise-style interface built with Plotly  / Streamlit.


---

## 💡 About the Project

Insider threats are among the most dangerous and hardest-to-detect risks for modern retail enterprises. Employees with access to sensitive systems or data can accidentally or maliciously cause major damage.

This project was developed to provide:
- ⚠️ **Early detection of suspicious behavior**
- 🧠 **Behavioral anomaly scoring using unsupervised learning**
- ⚡ **Fast querying and filtering using DuckDB**
- 📊 **Interactive dashboards with visual insights built in Streamlit**

---

## ✨ Features

### 🧠 Threat Detection Engine

- **Unsupervised Anomaly Scoring** using clustering or isolation-based techniques  
- **No labeled data required** – adapts to any enterprise dataset  
- **Risk Level Categorization**: Low, Medium, High based on behavior profiles  
- **Modular design** to easily swap/experiment with different ML models  

### 📊 Streamlit Dashboard

- **KPI Cards**: Total anomalies, high-risk users, activity count  
- **Interactive Filtering** by date, user ID, risk level, or activity type  
- **Visualizations**: Heatmaps, bar charts, anomaly timelines  
- **Data Export**: Filtered results downloadable as Excel (.xlsx)  
- **Dark Mode** compatible and responsive UI  

### 🦆 DuckDB Integration

- **Handles ~4M+ rows** effortlessly with in-memory SQL  
- **High-speed queries** on large datasets  
- **SQL + Python integration** for smooth backend logic  

---

## 🛠️ Tech Stack

| Component         | Technology                  |
|------------------|-----------------------------|
| Dashboard         | Streamlit                   |
| Database Engine   | DuckDB                      |
| ML Engine         | Scikit-learn, NumPy, pandas |
| Visualization     | Plotly, matplotlib          |
| Exporting         | OpenPyXL, Pandas Excel      |

---

## 📂 Dataset Downloads

The following datasets are used in the **Retail Insider Threat Detection System**. You can download them individually or visit the release page to access all files.

### 📦 Individual Files
- [📥 `logon.csv`](https://github.com/AnshikaRajput296/Retail-Threat-Detection/releases/download/v1.0-data/logon.csv)  
- [📥 `user_risk_analysis.csv`](https://github.com/AnshikaRajput296/Retail-Threat-Detection/releases/download/v1.0-data/user_risk_analysis.csv)  
- [📥 `device.csv`](https://github.com/AnshikaRajput296/Retail-Threat-Detection/releases/download/v1.0-data/device.csv)  
- [📥 `http.csv`](https://github.com/AnshikaRajput296/Retail-Threat-Detection/releases/download/v1.0-data/http.csv)

### 🔗 Full Release Page
👉 [**GitHub Release – v1.0-data**](https://github.com/AnshikaRajput296/Retail-Threat-Detection/releases/tag/v1.0-data)

