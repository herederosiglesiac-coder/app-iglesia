import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- Configuración ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")
URL_SHEET = "https://google.com"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Carga de Datos ---
@st.cache_data(ttl=30)
def load_sheet_data(worksheet_name):
    try:
        # Se forza la lectura directa con la URL proporcionada
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name)
    except Exception as e:
        st.error(f"Error al conectar con {worksheet_name}. Revisa los permisos.")
        return pd.DataFrame()

# Carga de hojas
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")
finanzas_df = load_sheet_data("FINANZAS")
chat_df = load_sheet_data("CHAT_LIDERES")
eventos_df = load_sheet_data("EVENTOS")

# --- Funciones de Interfaz ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: st.session_state.usuario = None
    if st.session_state.usuario is None:
        email = st.sidebar.text_input("Correo", key="login_email")
        password = st.sidebar.text_input("Contraseña", type="password", key="login_pass")
        if st.sidebar.button("Iniciar Sesión"):
            user = usuarios_df[(usuarios_df["Correo"].astype(str) == str(email)) & (usuarios_df["Contraseña"].astype(str) == str(password))]
            if not user.empty:
                st.session_state.usuario = user.iloc[0].to_dict()
                st.rerun()
            else: st.sidebar.error("Credenciales incorrectas.")
    else:
        st.sidebar.success(f"Hola: {st.session_state.usuario.get('Nombre')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    st.markdown("### 📅 Próximos Eventos")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            st.info(f"**{row.get('Fecha')}** - {row.get('Evento')}")
    st.markdown("---")
    st.subheader("🙏 Enviar Petición")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        peticion = st.text_area("Necesidad")
        if st.form_submit_button("Enviar"):
            nueva_fila = pd.DataFrame([{"Nombre": nombre or "Anónimo", "Peticion": peticion, "Fecha": datetime.now().strftime("%Y-%m-%d")}])
            updated_df = pd.concat([oraciones_df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="Oraciones", data=updated_df)
            st.success("Petición enviada.")

# --- Módulos (Consolidación, Finanzas, Chat) con actualización de URL ---
def panel_consolidacion():
    st.markdown("## 👥 Consolidación")
    with st.form("form_miembros", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo")
        if st.form_submit_button("Guardar"):
            nueva_fila = pd.DataFrame([{"Nombre Completo": nombre_m, "Estado": "Activo"}])
            updated_df = pd.concat([miembros_df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="MIEMBROS", data=updated_df)
            st.success("Registrado.")

def panel_financiero():
    st.markdown("## 💰 Finanzas")
    with st.form("form_finanzas", clear_on_submit=True):
        monto_f = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar"):
            nueva_fila = pd.DataFrame([{"Monto": monto_f, "Tipo": "Ingreso"}])
            updated_df = pd.concat([finanzas_df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="FINANZAS", data=updated_df)
            st.success("Registrado.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat")
    with st.form("form_chat", clear_on_submit=True):
        msg = st.text_input("Mensaje")
        if st.form_submit_button("Enviar"):
            nueva_fila = pd.DataFrame([{"Usuario": usuario_actual.get("Nombre"), "Mensaje": msg}])
            updated_df = pd.concat([chat_df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="CHAT_LIDERES", data=updated_df)
            st.rerun()

# --- Main ---
def main():
    usuario = autenticar()
    if usuario is None: vista_publica()
    else:
        opcion = st.sidebar.selectbox("Módulo", ["Inicio", "Consolidación", "Finanzas", "Chat"])
        if opcion == "Inicio": vista_publica()
        elif opcion == "Consolidación": panel_consolidacion()
        elif opcion == "Finanzas": panel_financiero()
        elif opcion == "Chat": sala_chat(usuario)

if __name__ == "__main__":
    main()
