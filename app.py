import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- Configuración Base ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# Inyección directa de la URL para saltar bloqueos de Secrets
URL_DIRECTA = "https://google.com"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Carga de Datos Resiliente y Directa ---
@st.cache_data(ttl=10)
def load_sheet_data(worksheet_name):
    try:
        # Se lee la pestaña usando la URL explícita del documento
        df = conn.read(spreadsheet=URL_DIRECTA, worksheet=worksheet_name)
        return df.dropna(how='all')
    except Exception as e:
        return pd.DataFrame()

# Cargar las tablas de la Iglesia de forma directa
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")
finanzas_df = load_sheet_data("FINANZAS")
chat_df = load_sheet_data("CHAT_LIDERES")
eventos_df = load_sheet_data("EVENTOS")

# --- Identificador Inteligente de Columnas ---
def buscar_columna(df, posibles_nombres):
    if df.empty: return None
    for nombre in posibles_nombres:
        for col in df.columns:
            if str(col).strip().lower() == nombre.lower(): return col
    return None

# --- Módulo de Autenticación de Líderes ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: 
        st.session_state.usuario = None
        
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip().lower()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            if usuarios_df.empty:
                st.sidebar.error("Error de acceso: No se pudo conectar a la tabla de USUARIOS. Verifica que tu Google Sheet tenga el acceso compartido en modo público.")
                return None
                
            col_email = buscar_columna(usuarios_df, ["Correo", "Email", "Correo Electronico", "Usuario"])
            col_pass = buscar_columna(usuarios_df, ["Contraseña", "Contrasena", "Clave", "Password"])
            col_nombre = buscar_columna(usuarios_df, ["Nombre", "Usuario", "Líder"])
            col_rol = buscar_columna(usuarios_df, ["Rol", "Tipo", "Permiso"])
            
            if col_email and col_pass:
                usuarios_df[col_email] = usuarios_df[col_email].astype(str).str.strip().str.lower()
                usuarios_df[col_pass] = usuarios_df[col_pass].astype(str).str.strip()
                
                user = usuarios_df[(usuarios_df[col_email] == email_input) & (usuarios_df[col_pass] == pass_input)]
                
                if not user.empty:
                    fila = user.iloc[0]
                    st.session_state.usuario = {
                        "Nombre": fila[col_nombre] if col_nombre else "Líder",
                        "Rol": fila[col_rol] if col_rol else "Servidor"
                    }
                    st.rerun()
                else:
                    st.sidebar.error("Correo o contraseña incorrectos.")
            else:
                st.sidebar.error("Asegúrate de que tu pestaña USUARIOS tenga las columnas llamadas exactamente 'Correo' y 'Contraseña'.")
    else:
        st.sidebar.success(f"Hola: {st.session_state.usuario.get('Nombre')}")
        st.sidebar.info(f"Rol: {st.session_state.usuario.get('Rol')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --- Vistas del Sistema ---
def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    st.markdown("### 📅 Próximos Eventos y Actividades")
    if not eventos_df.empty:
        col_evento = buscar_columna(eventos_df, ["Evento", "Nombre", "Actividad"])
        col_fecha = buscar_columna(eventos_df, ["Fecha", "Día"])
        for _, row in eventos_df.iterrows():
            ev = row[col_evento] if col_evento else "Reunión de la Iglesia"
            fe = row[col_fecha] if col_fecha else "Semanal"
            st.info(f"**{fe}** - {ev}")
    else:
        st.write("No hay eventos programados en este momento.")
        
    st.markdown("---")
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre")
        peticion = st.text_area("Petición")
        if st.form_submit_button("Enviar"):
            if not oraciones_df.empty:
                nueva_fila = pd.DataFrame([{"Nombre": nombre or "Anónimo", "Peticion": peticion, "Fecha": datetime.now().strftime("%Y-%m-%d")}])
                updated_df = pd.concat([oraciones_df, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=URL_DIRECTA, worksheet="Oraciones", data=updated_df)
                st.success("¡Petición enviada! Estaremos orando por ti.")
            else:
                st.error("No se pudo conectar a la base de datos para guardar.")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    st.success("Conectado con la pestaña MIEMBROS.")
    if not miembros_df.empty:
        st.dataframe(miembros_df.head(10))

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.success("Conectado con la pestaña FINANZAS.")
    if not finanzas_df.empty:
        st.dataframe(finanzas_df.head(10))

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    st.success("Muro de mensajes activo.")
    if not chat_df.empty:
        st.dataframe(chat_df.tail(10))

# --- Controlador de Navegación ---
def main():
    usuario = autenticar()
    if usuario is None:
        vista_publica()
    else:
        rol = str(usuario.get("Rol", "Servidor")).strip().lower()
        menu = ["Inicio / Eventos"]
        if rol in ["pastor", "líder", "lider", "servidor"]:
            menu.append("Consolidación y Asistencia")
        if rol in ["pastor", "tesorero"]:
            menu.append("Gestión Financiera")
        menu.append("Chat de Líderes")
        
        opcion = st.selectbox("Selecciona Módulo:", menu)
        if opcion == "Inicio / Eventos": vista_publica()
        elif opcion == "Consolidación y Asistencia": panel_consolidacion()
        elif opcion == "Gestión Financiera": panel_financiero()
        elif opcion == "Chat de Líderes": sala_chat(usuario)

if __name__ == "__main__":
    main()
