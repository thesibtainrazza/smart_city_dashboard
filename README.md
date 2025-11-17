# 🌆 Smart City IoT Dashboard

A fully interactive **Streamlit-based Smart City Dashboard** that visualizes real-time and historical **IoT sensor data** for environmental monitoring.  
This project showcases **data analytics**, **live simulation**, **air quality insights**, and a modern UI suitable for smart city applications.

---

## 🚀 Live Demo  
**🔗 https://smartcitydashboard.streamlit.app/**  
> Click above to view the deployed dashboard (hosted on Streamlit Cloud).

---

## 📌 Features

### ⭐ Interactive Dashboard
- Clean & responsive UI  
- Sidebar filters  
- Real-time IoT simulation  
- Interactive charts using Plotly  
- Dynamic KPIs  

### ⭐ Real-Time Sensor Simulation
Simulated IoT streams update every second for:
- Temperature  
- Humidity  
- AQI  
- PM2.5  
- PM10  
- CO  
- NO2  
- Wind speed  

### ⭐ Interactive Visualizations
Built with **Plotly** for:
- Line charts  
- Scatter comparisons  
- Bar charts  
- Correlation heatmap  
- Trend analysis  

### ⭐ Smart Alerts
Color-coded AQI alerts:
- 🟢 Good  
- 🟡 Moderate  
- 🟠 Unhealthy  
- 🔴 Hazardous  

### ⭐ Data Analytics
- Statistical summaries  
- Outlier detection  
- Correlation matrix  
- Distribution insights  

---

## 🧠 Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend UI** | Streamlit |
| **Visualization** | Plotly, Seaborn, Matplotlib |
| **Data Handling** | Pandas, NumPy |
| **Backend Logic** | Python |
| **Deployment** | Streamlit Cloud |
| **IoT Simulation** | Randomized sensor generator |

---

## 📊 Dataset Description

| Column Name | Description |
|-------------|-------------|
| Timestamp | Sensor timestamp |
| City | City name (Delhi, Bangalore) |
| Temperature(°C) | Temperature value |
| Humidity(%) | Humidity percentage |
| AQI | Air Quality Index |
| PM2.5 | Fine particulate matter µg/m³ |
| PM10 | Coarse particulate matter µg/m³ |
| CO(ppm) | Carbon monoxide in ppm |
| NO2(ppm) | Nitrogen dioxide in ppm |
| Wind Speed(km/h) | Wind speed |
| Weather | Categorical weather condition |

---

## 📁 Folder Structure

```bash
smart_city_dashboard/
│
├── app.py               # Main Streamlit application
├── data.csv             # IoT dataset (50 rows)
├── requirements.txt     # Dependencies for deployment
├── runtime.txt          # Python version (3.11 required for Streamlit Cloud)
│
├── plots/               # Pre-generated plots (optional)
└── README.md            # Documentation
```

---

## ⚙️ Installation (Run Locally)

### 1️⃣ Clone the repository:
```bash
git clone https://github.com/thesibtainrazza/smart_city_dashboard.git
cd smart_city_dashboard
```

### 2️⃣ Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate   # For Windows
```

### 3️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Streamlit app:
```bash
streamlit run app.py
```

---

## 🌐 Deployment (Streamlit Cloud)

This app is deployed using **Streamlit Cloud**, based on:

- `app.py`
- `requirements.txt`
- `runtime.txt` → forces Python **3.11**

### Deployment Steps:
1. Push project to GitHub  
2. Go to https://share.streamlit.io  
3. Click **New App**  
4. Select your repo → branch → `app.py`  
5. Deploy 🚀  

---

## 👨‍💻 Author

**Mohd. Sibtain Raza**  
Full-Stack Developer | IoT Enthusiast | Smart Solutions Maker  

🔗 GitHub: https://github.com/thesibtainrazza  
🔗 Smart City Dashboard: https://smartcitydashboard.streamlit.app/

---

## ⭐ Support  
If you like this project, please ⭐ star the repository — it motivates and helps the project grow!
