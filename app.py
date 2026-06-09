import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuración Base de la Pantalla ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- Datos de Prueba Integrados en Código (No requiere descargar de Google) ---
# Aquí puedes agregar manualmente más líderes si lo deseas en el futuro
USUARIOS_LOCALES = [
    {
        "Nombre_Completo": "Jose Perez",
        "Correo_Electronico": "perezajosef@gmail.com",
        "Contraseña": "pastor123",
        "Rol": "PASTOR"
    }
]

# --- Convertirlos en una Tabla Virtual ---
usuarios_df = pd.DataFrame(USUARIOS_LOCALES)

# Tablas vacías de respaldo por si el servidor requiere las variables
miembros_df = pd.DataFrame()
asistencia_df = pd.DataFrame()
oraciones_df = pd.DataFrame()
finanzas_df = pd.DataFrame()
chat_df = pd.DataFrame()
eventos_df = pd.DataFrame()

# --- Módulo de Autenticación de Líderes Local ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: 
        st.session_state.usuario = None
        
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip().lower()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            # Buscar concordancia directamente en la tabla integrada del código
            user = usuarios_df[
                (usuarios_df["Correo_Electronico"] == email_input) & 
                (usuarios_df["Contraseña"] == pass_input)
            ]
            
            if not user.empty:
                fila = user.iloc[0]
                st.session_state.usuario = {
                    "Nombre": fila["Nombre_Completo"],
                    "Rol": fila["Rol"]
                }
                st.rerun()
            else:
                st.sidebar.error("Correo o contraseña incorrectos.")
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
    st.info("Reunión General todos los Domingos - 10:00 AM")
        
    st.markdown("---")
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre")
        peticion = st.text_area("Petición")
        if st.form_submit_button("Enviar"):
            st.success("¡Petición procesada en el sistema!")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    st.success("Panel de administración activo. Interfaz lista para operar.")
    st.write("Aquí podrás registrar nuevos creyentes e históricos.")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.success("Panel financiero activo. Control de ingresos y egresos.")
    st.write("Acceso exclusivo para rol de Pastor y Tesoreros.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    st.success("Muro de mensajes activo para coordinación.")
    st.write(f"Conectado como: {usuario_actual.get('Nombre')}")

# --- Controlador Central ---
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
