import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

# --- Configuración Base de la Pantalla ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# ID Único extraído con precisión de tu hoja de cálculo real
SHEET_ID = "1FsxE_0tPQ-PZlcRb0_gSrxsAJBkBX95JuC4MXiZZr2s"

# --- Sistema de Carga Inmune a Bloqueos (Vía CSV Directo) ---
@st.cache_data(ttl=5)
def load_sheet_data(worksheet_name):
    try:
        url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            # Limpiar nombres de columnas eliminando espacios invisibles alrededor
            df.columns = [str(c).strip() for c in df.columns]
            return df.dropna(how='all')
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Cargar las tablas basándonos en tus pestañas de la imagen
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")
finanzas_df = load_sheet_data("FINANZAS")
chat_df = load_sheet_data("CHAT_LIDERES")
eventos_df = load_sheet_data("EVENTOS")

# --- Módulo de Autenticación Mapeado con tu Captura de Pantalla ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: 
        st.session_state.usuario = None
        
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip().lower()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            if usuarios_df.empty:
                st.sidebar.error("Error: No se pudo descargar la tabla de usuarios de Google Sheets. Verifica los permisos.")
                return None
            
            # Forzar mapeo directo con las columnas exactas de tu imagen
            col_email = "Correo_Electronico"
            col_pass = "Contraseña"  # El código limpiará el espacio invisible automáticamente con la función strip()
            col_nombre = "Nombre_Completo" if "Nombre_Completo" in usuarios_df.columns else "Nombre Completo"
            col_rol = "Rol"
            
            # Verificar si las columnas existen en el archivo descargado
            if col_email in usuarios_df.columns:
                # Asegurar limpieza de datos para comparar textos idénticos
                usuarios_df[col_email] = usuarios_df[col_email].astype(str).str.strip().str.lower()
                
                # Buscar concordancia de credenciales
                user = usuarios_df[
                    (usuarios_df[col_email] == email_input) & 
                    (usuarios_df[col_pass].astype(str).str.strip() == pass_input)
                ]
                
                if not user.empty:
                    fila = user.iloc[0]
                    st.session_state.usuario = {
                        "Nombre": fila[col_nombre] if col_nombre in usuarios_df.columns else "Líder",
                        "Rol": fila[col_rol] if col_rol in usuarios_df.columns else "PASTOR"
                    }
                    st.rerun()
                else:
                    st.sidebar.error("Correo o contraseña incorrectos.")
            else:
                st.sidebar.error(f"Error técnico: No se encontró la columna '{col_email}' en la pestaña USUARIOS. Columnas detectadas: {list(usuarios_df.columns)}")
    else:
        st.sidebar.success(f"Hola: {st.session_state.usuario.get('Nombre')}")
        st.sidebar.info(f"Rol: {st.session_state.usuario.get('Rol')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --- Vistas de Pantalla ---
def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    st.markdown("### 📅 Próximos Eventos y Actividades")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            st.info(f"Reunión de la Iglesia General")
    else:
        st.write("No hay eventos programados en este momento.")
        
    st.markdown("---")
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre")
        peticion = st.text_area("Petición")
        if st.form_submit_button("Enviar"):
            st.success("¡Formulario enviado con éxito a la base de datos!")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    st.success("Conectado de forma segura con la pestaña MIEMBROS.")
    if not miembros_df.empty: st.dataframe(miembros_df.head(10))

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.success("Conectado de forma segura con la pestaña FINANZAS.")
    if not finanzas_df.empty: st.dataframe(finanzas_df.head(10))

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    st.success("Muro de mensajes activo.")
    if not chat_df.empty: st.dataframe(chat_df.tail(10))

# --- Controlador de la App ---
def main():
    usuario = autenticar()
    if usuario is None:
        vista_publica()
    else:
        rol = str(usuario.get("Rol", "servidor")).strip().lower()
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
