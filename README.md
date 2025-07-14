# 🔐 Retail Insider Threat Detection 🛒🧠  
**Scalable Risk Analytics Dashboard | Unsupervised Learning + DuckDB + Streamlit**

Welcome to the **Retail Insider Threat Detection System**, a powerful and interactive cybersecurity analytics dashboard designed to identify potential insider threats in large-scale retail environments. Using **unsupervised learning techniques**, high-performance **DuckDB querying**, and an intuitive **Streamlit UI**, this project enables real-time anomaly detection from millions of activity logs.

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
| Visualization     | Plotly, Altair              |
| Exporting         | OpenPyXL, Pandas Excel      |

---
