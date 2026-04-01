import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# 1. Konfigurasi Halaman (Tema Biru khas Industry 5.0)
st.set_page_config(page_title="AI-BI Dashboard Industry 5.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# 2. Dataset Dummy (Simulasi Data Operasional/Jasa)
@st.cache_data
def load_data():
    data = {
        'Bulan': np.arange(1, 13),
        'Permintaan_Aktual': [150, 165, 170, 190, 185, 210, 230, 240, 220, 250, 270, 290]
    }
    return pd.DataFrame(data)

df = load_data()

# 3. Engine AI Forecasting (Linear Regression)
def run_ai_forecast(df):
    X = df[['Bulan']]
    y = df['Permintaan_Aktual']
    model = LinearRegression()
    model.fit(X, y)
    
    # Prediksi bulan ke-13
    next_month = np.array([[13]])
    prediction = model.predict(next_month)[0]
    return round(prediction, 2)

ai_pred = run_ai_forecast(df)

# 4. Antarmuka Dashboard
st.title("📊 BI Dashboard: Human-AI Collaboration System")
st.subheader("Optimasi Strategis Berbasis Industry 5.0")
st.write("---")

# Layout Kolom
col1, col2 = st.columns([1, 2])

with col1:
    st.info("### 🤖 AI Insight")
    st.metric(label="Prediksi AI (Bulan Depan)", value=f"{ai_pred} Unit")
    st.write("Model: *Linear Regression*")
    
    st.write("---")
    st.warning("### 👤 Human Intervention (Override)")
    st.write("Gunakan intuisi manajerial untuk menyesuaikan hasil prediksi berdasarkan kondisi lapangan.")
    
    # Fitur Manual Override
    override_val = st.slider("Penyesuaian Manusia (%)", -50, 50, 0)
    final_decision = round(ai_pred * (1 + override_val/100), 2)
    
    st.success(f"### 🎯 Keputusan Akhir: {final_decision} Unit")

with col2:
    # Visualisasi Data
    fig = go.Figure()
    # Data Aktual
    fig.add_trace(go.Scatter(x=df['Bulan'], y=df['Permintaan_Aktual'], name='Data Aktual', line=dict(color='blue', width=3)))
    # Titik Prediksi Akhir
    fig.add_trace(go.Scatter(x=[13], y=[final_decision], name='Keputusan (AI + Human)', mode='markers', marker=dict(color='red', size=15)))
    
    fig.update_layout(title="Tren Permintaan & Prediksi", xaxis_title="Bulan", yaxis_title="Volume", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# 5. Logika Optimasi (Engineering Logic)
st.write("---")
st.write("### ⚙️ Rekomendasi Optimasi Strategis")
c1, c2, c3 = st.columns(3)

# Contoh rumus TI: Safety Stock (Sederhana)
safety_stock = round(final_decision * 0.1, 2) 

with c1:
    st.write("**Rencana Produksi/Layanan**")
    st.code(f"{final_decision} Unit")
with c2:
    st.write("**Safety Stock (10%)**")
    st.code(f"{safety_stock} Unit")
with c3:
    st.write("**Total Alokasi Sumber Daya**")
    st.code(f"{final_decision + safety_stock} Unit")

st.write("---")
st.caption("Skripsi Teknik Industri - Implementasi Industry 5.0 Framework")