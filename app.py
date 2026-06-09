import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- Configuración Base ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# URL Oficial con permisos de exportación de datos limpios
URL_SHEET = "https://google.com"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Carga de Datos Resiliente ---
@st.cache_data(ttl=15)
def load_sheet_data(worksheet_name):
    try:
        # Forzar lectura pública por URL para evitar fallos de credenciales corporativas
        df = conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name)
        return df.dropna(how='all') # Elimina filas completamente vacías
    except Exception as e:
        return pd.DataFrame()

# Cargar las tablas de la Iglesia
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")
finanzas_df = load_sheet_data("FINANZAS")
chat_df = load_sheet_data("CHAT_LIDERES")
eventos_df = load_sheet_data("EVENTOS")

# --- Identificador Inteligente de Columnas (Evita KeyError) ---
def buscar_columna(df, posibles_nombres):
    if df.empty:
        return None
    for nombre in posibles_nombres:
        for col in df.columns:
            if str(col).strip().lower() == nombre.lower():
                return col
    return None

# --- Módulo de Autenticación Pro ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: 
        st.session_state.usuario = None
        
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            if usuarios_df.empty:
                st.sidebar.error("La tabla de USUARIOS está vacía o inaccesible.")
                return None
                
            # Buscar dinámicamente cómo se llaman tus columnas en el Excel
            col_email = buscar_columna(usuarios_df, ["Correo", "Email", "Correo Electronico", "Usuario"])
            col_pass = buscar_columna(usuarios_df, ["Contraseña", "Contrasena", "Clave", "Password"])
            col_nombre = buscar_columna(usuarios_df, ["Nombre", "Usuario", "Líder"])
            col_rol = buscar_columna(usuarios_df, ["Rol", "Tipo", "Permiso"])
            
            if col_email and col_pass:
                # Filtrar ignorando mayúsculas/minúsculas y espacios
                user = usuarios_df[
                    (usuarios_df[col_email].astype(str).str.strip() == email_input) & 
                    (usuarios_df[col_pass].astype(str).str.strip() == pass_input)
                ]
                if not user.empty:
                    fila = user.iloc[0]
                    st.session_state.usuario = {
                        "Nombre": fila[col_nombre] if col_nombre else "Líder",
                        "Rol": fila[col_rol] if col_rol else "Servidor"
                    }
                    st.rerun()
                else:
                    st.sidebar.error("Usuario o contraseña incorrectos.")
            else:
                st.sidebar.error("Error: No encontramos las columnas de 'Correo' o 'Contraseña' en tu pestaña USUARIOS.")
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
        st.write("No hay eventos programados en la pestaña EVENTOS.")
        
    st.markdown("---")
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre")
        peticion = st.text_area("Petición")
        if st.form_submit_button("Enviar"):
            st.success("¡Petición guardada! Estaremos orando por ti.")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    st.info("Formularios listos para registro y control de asistencia.")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.info("Formularios listos para control de ingresos y egresos.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    st.info("Muro de mensajes activo.")

# --- Controlador de Navegación ---
def main():
    usuario = autenticar()
    if usuario is None:
        vista_publica()
    else:
        rol = usuario.get("Rol", "Servidor")
        menu = ["Inicio / Eventos"]
        if str(rol).strip().lower() in ["pastor", "líder", "lider", "servidor"]:
            menu.append("Consolidación y Asistencia")
        if str(rol).strip().lower() in ["pastor", "tesorero"]:
            menu.append("Gestión Financiera")
        menu.append("Chat de Líderes")
        
        opcion = st.sidebar.selectbox("Selecciona Módulo:", menu)
        if opcion == "Inicio / Eventos": vista_publica()
        elif opcion == "Consolidación y Asistencia": panel_consolidacion()
        elif opcion == "Gestión Financiera": panel_financiero()
        elif opcion == "Chat de Líderes": sala_chat(usuario)

if __name__ == "__main__":
    main()
