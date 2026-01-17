import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Visor de Arriendos", page_icon="🏢", layout="centered")

# --- CSS PARA QUE SE VEA COMO TU EXCEL ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .stSuccess { background-color: #d4edda; color: #155724; }
    .stWarning { background-color: #fff3cd; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGAR DATOS ---
# REEMPLAZA ESTO CON TU ID DE GOOGLE SHEET
sheet_id = "1nnjC9NUteYImRbxBeAgcY3ORdzvuI5MUhV_lnUxauNo" 
sheet_name = "Hoja 3" 
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(url)
        # Limpieza de datos numéricos (quita signos $ y puntos si los hubiera)
        cols_money = ['Canon', 'Total_Pago_Arriendo', 'Admin_Monto', 'Total_Descuento', 'Total_a_Transferir']
        for col in cols_money:
            if col in data.columns:
                data[col] = data[col].astype(str).str.replace(r'[$,.]', '', regex=True)
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        return data
    except Exception as e:
        return None

df = load_data()

# --- INTERFAZ ---
st.title("🏢 Gestión de Propiedades")

if df is not None:
    # 1. SELECTOR DE DEPARTAMENTO (Solo muestra tus deptos: 403 A, 803 OPA, etc.)
    deptos = df['Depto'].unique()
    depto_seleccionado = st.selectbox("Selecciona el Departamento:", deptos)

    # Filtrar datos
    try:
        fila = df[df['Depto'] == depto_seleccionado].iloc[0]
        
        st.markdown("---")

        # 2. SECCIÓN: DATOS DEPARTAMENTO (Igual a tu imagen 1)
        st.subheader("Datos Departamento:")
        
        with st.container():
            col_a, col_b = st.columns(2)
            with col_a:
                st.text_input("Edificio/Comunidad", value=fila['Edificio'], disabled=True)
                st.text_input("Dirección", value=fila['Direccion'], disabled=True)
                st.text_input("Departamento", value=fila['Depto'], disabled=True)
                st.text_input("Nombre Propietario", value=fila['Propietario'], disabled=True)
            
            with col_b:
                st.text_input("Nombre Arrendatario", value=fila['Arrendatario'], disabled=True)
                st.text_input("Fecha Inicio Contrato", value=fila['Fecha_Inicio'], disabled=True)
                st.text_input("Fecha Vencimiento Contrato", value=fila['Fecha_Vencimiento'], disabled=True)
                # Formato moneda chilena
                canon_fmt = "${:,.0f}".format(fila['Canon']).replace(",", ".")
                st.text_input("Canon de arriendo", value=canon_fmt, disabled=True)

        st.markdown("---")

        # 3. SECCIÓN: DETALLE ARRIENDO (Igual a tu imagen 2)
        st.subheader("Detalle Arriendo:")
        
        # El título del mes dinámico
        st.markdown(f"### 📅 {fila['Mes']}")
        
        col_fin, col_comp = st.columns([1, 1])
        
        with col_fin:
            # Cálculos visuales
            pago_fmt = "${:,.0f}".format(fila['Total_Pago_Arriendo']).replace(",", ".")
            st.metric("Total Pago Arriendo", pago_fmt)
            
            admin_fmt = "${:,.0f}".format(fila['Admin_Monto']).replace(",", ".")
            st.metric(f"Administración 0,8% {fila['Mes']}", admin_fmt)
            
            # Bloque Verde (Descuento)
            desc_fmt = "${:,.0f}".format(fila['Total_Descuento']).replace(",", ".")
            st.success(f"**Total Descuento: {desc_fmt}**")
            
            # Bloque Amarillo (Total a Transferir)
            transfer_fmt = "${:,.0f}".format(fila['Total_a_Transferir']).replace(",", ".")
            st.warning(f"👉 **TOTAL A TRANSFERIR: {transfer_fmt}**")

        with col_comp:
            st.write("Comprobante:")
            if pd.notna(fila['Link_Comprobante']) and str(fila['Link_Comprobante']).startswith('http'):
                st.image(fila['Link_Comprobante'], caption="Comprobante Adjunto", use_column_width=True)
            else:
                st.info("No hay comprobante cargado.")

    except IndexError:
        st.error("Error: No se encontraron datos para este departamento.")
else:

    st.error("No se pudo cargar la base de datos. Revisa el link de Google Sheets.")
