import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA BIRU
# ==========================================
st.set_page_config(page_title="Dashboard BI - Industry 5.0", page_icon="⚙️", layout="wide")

# Custom CSS untuk tampilan ala Power BI (Card Biru, Shadow, Clean Look)
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    div.css-1r6slb0.e1tzin5v2 { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-card { background-color: #0052cc; color: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-title { font-size: 16px; font-weight: bold; opacity: 0.9; }
    .metric-value { font-size: 28px; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNGSI PENGOLAHAN DATA
# ==========================================
@st.cache_data
def load_default_data():
    # Data default bertema otomotif jika tidak ada file yang diunggah
    data = {
        'Periode': np.arange(1, 25),
        'Bulan': pd.date_range(start='2024-01-01', periods=24, freq='M').strftime('%b %Y'),
        'Permintaan': [120, 135, 125, 145, 160, 155, 170, 185, 175, 195, 210, 205, 
                       220, 235, 225, 250, 265, 255, 275, 290, 280, 310, 325, 315]
    }
    return pd.DataFrame(data)

def process_uploaded_file(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file)
    
    # Asumsi kolom: harus ada kolom yang bisa diplot (mengambil kolom numerik terakhir sebagai target)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) < 1:
        st.error("File harus memiliki setidaknya satu kolom angka (numerik) untuk dianalisis.")
        return None
    
    # Membuat kolom 'Periode' otomatis sebagai urutan waktu
    df['Periode'] = np.arange(1, len(df) + 1)
    df['Target_Value'] = df[num_cols[-1]] # Menggunakan kolom numerik terakhir sebagai target
    
    # Jika ada kolom tanggal, gunakan itu. Jika tidak, buat indeks.
    date_cols = df.select_dtypes(include=['object', 'datetime']).columns.tolist()
    if date_cols:
        df['Label_Waktu'] = df[date_cols[0]].astype(str)
    else:
        df['Label_Waktu'] = "Periode " + df['Periode'].astype(str)
        
    return df

# ==========================================
# 3. SIDEBAR: UPLOAD & KONTROL MANUSIA
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2082/2082184.png", width=60)
    st.title("Panel Kendali")
    st.write("---")
    
    st.header("📂 1. Input Data")
    uploaded_file = st.file_uploader("Unggah File Data (Excel/CSV)", type=['csv', 'xlsx'])
    
    st.write("---")
    st.header("⚙️ 2. Parameter Optimasi")
    lead_time = st.number_input("Lead Time (Hari/Minggu)", min_value=1, value=5)
    service_level = st.slider("Service Level (%)", 80, 99, 95)
    
    st.write("---")
    st.header("👤 3. Manual Override")
    st.info("Koreksi hasil AI berdasarkan insting manajerial & kondisi eksternal.")
    override_pct = st.slider("Penyesuaian Ahli (%)", -50, 50, 0)

# ==========================================
# 4. INISIALISASI DATASET
# ==========================================
if uploaded_file is not None:
    df = process_uploaded_file(uploaded_file)
    target_col = 'Target_Value'
    time_label = 'Label_Waktu'
    st.sidebar.success(f"File {uploaded_file.name} berhasil dimuat!")
else:
    df = load_default_data()
    target_col = 'Permintaan'
    time_label = 'Bulan'
    st.sidebar.warning("Menggunakan Data Default (Belum ada file diunggah).")

if df is not None:
    # ==========================================
    # 5. ENGINE AI - FORECASTING (Linear Regression)
    # ==========================================
    X = df[['Periode']]
    y = df[target_col]
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Prediksi periode berikutnya
    next_period = np.array([[len(df) + 1]])
    ai_raw_pred = model.predict(next_period)[0]
    
    # Logika Manual Override (Industry 5.0)
    final_decision = ai_raw_pred * (1 + (override_pct / 100))
    
    # Kalkulasi Teknik Industri (Safety Stock & ROP)
    # Z-Score sederhana untuk service level
    z_dict = {80: 0.84, 85: 1.04, 90: 1.28, 95: 1.65, 99: 2.33}
    z_score = z_dict.get(service_level, 1.65)
    std_dev = np.std(y)
    
    safety_stock = z_score * std_dev * np.sqrt(lead_time)
    rop = (final_decision / 30 * lead_time) + safety_stock # Asumsi 30 hari/bulan

    # ==========================================
    # 6. TATA LETAK UTAMA (TABS)
    # ==========================================
    st.title("💼 Business Intelligence Dashboard")
    st.markdown("Sistem Pengambilan Keputusan Strategis Kolaborasi AI dan Manusia (Industry 5.0)")
    
    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📈 AI & Human Forecasting", "📑 Raw Data & Audit"])
    
    # -------- TAB 1: EXECUTIVE SUMMARY --------
    with tab1:
        st.markdown("### Key Performance Indicators (KPI)")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Prediksi Murni AI</div>
                <div class="metric-value">{int(ai_raw_pred)}</div>
            </div>""", unsafe_allow_html=True)
            
        with c2:
            # Berubah warna jika di-override
            bg_color = "#e63946" if override_pct != 0 else "#0052cc"
            st.markdown(f"""
            <div class="metric-card" style="background-color: {bg_color};">
                <div class="metric-title">Keputusan Final (Override)</div>
                <div class="metric-value">{int(final_decision)}</div>
            </div>""", unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Target Safety Stock</div>
                <div class="metric-value">{int(safety_stock)}</div>
            </div>""", unsafe_allow_html=True)
            
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Reorder Point (ROP)</div>
                <div class="metric-value">{int(rop)}</div>
            </div>""", unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)
        
        # Grafik Utama Ala Power BI
        fig_main = go.Figure()
        fig_main.add_trace(go.Scatter(x=df[time_label], y=df[target_col], 
                                      mode='lines+markers', name='Data Aktual',
                                      line=dict(color='#0052cc', width=3)))
                                      
        # Titik Prediksi
        fig_main.add_trace(go.Scatter(x=[f"Periode {len(df)+1}"], y=[final_decision], 
                                      mode='markers', name='Keputusan Final (AI+Human)',
                                      marker=dict(color='#e63946', size=15, symbol='star')))
                                      
        fig_main.update_layout(title="Tren Performa Historis vs Keputusan Masa Depan",
                               plot_bgcolor='white', hovermode="x unified",
                               xaxis=dict(showgrid=True, gridcolor='lightgray'),
                               yaxis=dict(showgrid=True, gridcolor='lightgray'))
        st.plotly_chart(fig_main, use_container_width=True)

    # -------- TAB 2: AI & HUMAN FORECASTING --------
    with tab2:
        colA, colB = st.columns([1, 1])
        
        with colA:
            st.subheader("Distribusi Data (Measure Phase)")
            fig_hist = px.histogram(df, x=target_col, nbins=10, 
                                    color_discrete_sequence=['#0052cc'],
                                    title="Distribusi Frekuensi Data")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with colB:
            st.subheader("Dampak Intervensi Manusia")
            impact_data = pd.DataFrame({
                "Skenario": ["1. Prediksi AI", "2. Keputusan Manusia (Final)"],
                "Nilai": [ai_raw_pred, final_decision]
            })
            fig_bar = px.bar(impact_data, x="Skenario", y="Nilai", color="Skenario",
                             color_discrete_map={"1. Prediksi AI": "#0052cc", "2. Keputusan Manusia (Final)": "#e63946"},
                             title="Perbandingan AI vs Human Decision")
            st.plotly_chart(fig_bar, use_container_width=True)

        st.info(f"**Insight:** Dengan mengaktifkan intervensi sebesar **{override_pct}%**, parameter persediaan seperti Safety Stock dan Reorder Point secara otomatis beradaptasi dengan tingkat ketidakpastian lapangan, menjaga keseimbangan operasional yang *Lean*.")

    # -------- TAB 3: RAW DATA & AUDIT --------
    with tab3:
        st.subheader("Tabel Audit Data Terintegrasi")
        st.dataframe(df.style.background_gradient(cmap='Blues'), use_container_width=True)
        
        # Tombol Download untuk Laporan
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Data Historis (CSV)",
            data=csv,
            file_name='data_audit_export.csv',
            mime='text/csv',
        )
