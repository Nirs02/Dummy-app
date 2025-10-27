%%writefile aoc_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# ===============================
# KONFIGURASI AWAL
# ===============================
st.set_page_config(page_title="Dashboard AoC", layout="wide")

# ===============================
# CEK DATA LOKAL
# ===============================
if os.path.exists("data_progress.csv"):
    progress_df = pd.read_csv("data_progress.csv")
else:
    progress_df = pd.DataFrame(columns=[
        "Bulan", "Unit Kerja", "Tim AoC", "Program Kerja AoC",
        "Dampak Terhadap Pelayanan", "Upaya Perbaikan"
    ])

# ===============================
# DATA USER LOGIN
# ===============================
USERS = {
    "admin": {"password": "12345", "role": "admin", "unit": "Semua Unit"},
    "pegawai1": {"password": "aoc2025", "role": "user", "unit": "Instalasi Rawat Jalan + Tim Kerja Humas"},
    "pegawai2": {"password": "aoc2025", "role": "user", "unit": "Instalasi Farmasi"}
}

# ===============================
# STATE LOGIN
# ===============================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "unit" not in st.session_state:
    st.session_state["unit"] = None

# ===============================
# FORM LOGIN
# ===============================
if not st.session_state["logged_in"]:
    st.title("🔐 Login Dashboard AoC")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = USERS[username]["role"]
            st.session_state["unit"] = USERS[username]["unit"]
            st.success(f"✅ Selamat datang, {username}!")
            st.experimental_rerun()
        else:
            st.error("Username atau password salah.")
    st.stop()

# ===============================
# LOGOUT
# ===============================
st.sidebar.write(f"👋 Login sebagai: **{st.session_state['username']}** ({st.session_state['role']})")
if st.sidebar.button("🚪 Logout"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()

# ===============================
# DATA DUMMY DASBOR
# ===============================
np.random.seed(42)
bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
unit_kerja = [
    "Instalasi Rawat Jalan + Tim Kerja Humas", "Instalasi Gawat Darurat + KSM Umum",
    "Instalasi Rawat Inap", "Instalasi Radiologi", "Instalasi Laboratorium Terpadu",
    "Instalasi Farmasi", "Instalasi Rehabilitasi Medik", "Instalasi Rekam Medik", "IVPP",
    "Tim Kerja TURT dan IKLK3 RS", "KSM Ilmu Kesehatan Anak", "KSM Spesialis Lain",
    "KSM Anestesiologi dan Terapi Intensif", "KSM Gigi dan Mulut"
]

data = []
for b in bulan:
    for u in unit_kerja:
        status = np.random.choice(["Sudah Upload", "Belum Upload"], p=[0.75, 0.25])
        peserta = np.random.randint(20, 100)
        data.append([b, u, f"Program {b} - {u}", status, peserta])

df = pd.DataFrame(data, columns=["Bulan", "Unit Kerja", "Nama Program", "Status Upload", "Jumlah Pegawai"])

# ===============================
# SIMPAN SESSION STATE LAPORAN
# ===============================
if "progress_df" not in st.session_state:
    st.session_state["progress_df"] = progress_df

# ===============================
# MENU SIDEBAR
# ===============================
if st.session_state["role"] == "admin":
    menu_list = [
        "🏠 Dashboard Utama",
        "📆 Rekap Tahunan",
        "📋 Detail Program",
        "🏆 Leaderboard AoC",
        "⚠️ Notifikasi Belum Upload",
        "📝 Input Laporan Kegiatan",
        "📥 Download Laporan",
        "💡 Saran Menu Dashboard",
        "🧰 Admin Panel"
    ]
else:
    menu_list = ["🏠 Dashboard Utama", "📝 Input Laporan Kegiatan"]

st.sidebar.title("📂 Menu Dashboard AoC")
menu = st.sidebar.radio("Pilih Halaman:", menu_list)

# ===============================
# DASHBOARD UTAMA
# ===============================
if menu == "🏠 Dashboard Utama":
    st.title("📊 Dashboard Utama Program Agent of Change (AoC)")

    total_unit = df["Unit Kerja"].nunique()
    sudah_upload_unit = df[df["Status Upload"] == "Sudah Upload"]["Unit Kerja"].unique()
    jumlah_sudah_upload = len(sudah_upload_unit)
    semua_unit = set(df["Unit Kerja"].unique())
    belum_upload_unit = semua_unit - set(sudah_upload_unit)
    jumlah_belum_upload = len(belum_upload_unit)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Unit", total_unit)
    col2.metric("Sudah Upload", jumlah_sudah_upload)
    col3.metric("Belum Upload", jumlah_belum_upload)

    trend = (
        df[df["Status Upload"] == "Sudah Upload"]
        .groupby("Bulan")["Unit Kerja"]
        .nunique()
        .reset_index()
    )
    trend = trend.sort_values("Bulan", key=lambda x: pd.Categorical(x, categories=bulan, ordered=True))
    fig1 = px.line(trend, x="Bulan", y="Unit Kerja", markers=True,
                   title="📈 Tren Unit Kerja yang Sudah Upload per Bulan")
    st.plotly_chart(fig1, use_container_width=True)

# ===============================
# INPUT LAPORAN
# ===============================
elif menu == "📝 Input Laporan Kegiatan":
    st.title("📝 Form Laporan Kegiatan AoC")

    with st.form("laporan_form"):
        bulan_input = st.selectbox("Bulan Kegiatan", bulan)
        if st.session_state["role"] == "admin":
            unit_input = st.selectbox("Pilih Unit Kerja", unit_kerja)
        else:
            unit_input = st.session_state["unit"]
            st.markdown(f"**Unit Kerja:** {unit_input}")

        program_input = st.text_area("Program AoC")
        dampak_input = st.text_area("Dampak Terhadap Pelayanan")
        upaya_input = st.text_area("Upaya Perbaikan Selanjutnya")
        submitted = st.form_submit_button("💾 Simpan Laporan")

        if submitted:
            new_entry = pd.DataFrame([{
                "Bulan": bulan_input,
                "Unit Kerja": unit_input,
                "Tim AoC": st.session_state["username"],
                "Program Kerja AoC": program_input,
                "Dampak Terhadap Pelayanan": dampak_input,
                "Upaya Perbaikan": upaya_input
            }])
            st.session_state["progress_df"] = pd.concat([st.session_state["progress_df"], new_entry], ignore_index=True)
            st.session_state["progress_df"].to_csv("data_progress.csv", index=False)
            st.success("✅ Laporan kegiatan berhasil disimpan!")

    st.markdown("#### 📋 Laporan yang sudah diinput:")
    if st.session_state["role"] == "admin":
        st.dataframe(st.session_state["progress_df"], use_container_width=True)
    else:
        df_user = st.session_state["progress_df"]
        df_user = df_user[df_user["Tim AoC"] == st.session_state["username"]]
        st.dataframe(df_user, use_container_width=True)

# ===============================
# MENU ADMIN KHUSUS
# ===============================
elif st.session_state["role"] == "admin":
    if menu == "📆 Rekap Tahunan":
        st.title("📆 Rekap Tahunan Program AoC")
        yearly = df.groupby(["Bulan", "Status Upload"]).size().reset_index(name="Jumlah")
        yearly = yearly.sort_values("Bulan", key=lambda x: pd.Categorical(x, categories=bulan, ordered=True))
        fig = px.bar(yearly, x="Bulan", y="Jumlah", color="Status Upload", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "📋 Detail Program":
        st.title("📋 Detail Program AoC")
        bulan_pilih = st.selectbox("Pilih Bulan:", bulan)
        st.dataframe(df[df["Bulan"] == bulan_pilih], use_container_width=True)

    elif menu == "🏆 Leaderboard AoC":
        st.title("🏆 Leaderboard Unit Kerja Aktif")
        leaderboard = df[df["Status Upload"] == "Sudah Upload"].groupby("Unit Kerja").size().reset_index(name="Jumlah Upload")
        leaderboard = leaderboard.sort_values("Jumlah Upload", ascending=False)
        st.dataframe(leaderboard, use_container_width=True)
        fig = px.bar(leaderboard, x="Unit Kerja", y="Jumlah Upload", color="Unit Kerja")
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "⚠️ Notifikasi Belum Upload":
        st.title("⚠️ Unit Kerja Belum Upload Program")
        belum_df = df[df["Status Upload"] == "Belum Upload"]
        if belum_df.empty:
            st.success("🎉 Semua unit kerja telah melakukan upload program AoC!")
        else:
            st.dataframe(belum_df, use_container_width=True)

    elif menu == "📥 Download Laporan":
        st.title("📥 Download Laporan")
        csv = st.session_state["progress_df"].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Rekap Laporan AoC", csv, "laporan_aoc.csv", "text/csv")

    elif menu == "💡 Saran Menu Dashboard":
        st.title("💡 Saran Menu Dashboard Tambahan")
        st.markdown("""
        | Menu | Fungsi | Keterangan |
        |------|---------|------------|
        | **Dashboard Utama** | Ringkasan capaian bulanan | Grafik dan status upload |
        | **Rekap Tahunan** | Analisis tren 12 bulan | Line chart atau heatmap |
        | **Detail Program** | Deskripsi & foto kegiatan | Bisa diakses per unit kerja |
        | **Leaderboard AoC** | Unit kerja paling aktif | Berdasarkan jumlah program |
        | **Notifikasi Belum Upload** | List otomatis unit kerja belum mengirim | Bisa ekspor ke Excel |
        | **Download Laporan** | Ekspor PDF/Excel ringkasan data | Untuk laporan ke pimpinan |
        | **Admin Panel** | Tambah/edit data manual | Khusus admin/verifikator |
        """)

    elif menu == "🧰 Admin Panel":
        st.title("🧰 Admin Panel - Edit Data Manual")
        st.info("Gunakan halaman ini untuk menambah, mengedit, atau menghapus laporan AoC secara manual.")

        df_edit = st.session_state["progress_df"].copy()
        edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Simpan Perubahan Data"):
            st.session_state["progress_df"] = edited_df
            edited_df.to_csv("data_progress.csv", index=False)
            st.success("✅ Perubahan berhasil disimpan!")
