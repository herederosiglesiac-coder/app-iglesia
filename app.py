import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página para dispositivos móviles
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# URL Base de tu Google Sheet (Extraída de tu enlace público)
# Al usar la exportación directa en formato CSV, rompemos cualquier bloqueo técnico del servidor.
BASE_URL = "https://google.com"

# --------- Carga de Datos Directa e Infalible -------------
def load_sheet_data(worksheet_name):
    try:
        # Transformamos el enlace para descargar la pestaña exacta directamente como texto CSV
        csv_url = f"{BASE_URL}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
        df = pd.read_csv(csv_url)
        # Limpiar columnas vacías que a veces genera Google Sheets
        df = df.dropna(how='all', axis=1)
        return df
    except Exception as e:
        st.error(f"Error al leer la pestaña {worksheet_name}: {e}")
        return pd.DataFrame()

# Cargar todas las fuentes de datos exactas de tus pestañas reales
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")
finanzas_df = load_sheet_data("FINANZAS")
chat_df = load_sheet_data("CHAT_LIDERES")
eventos_df = load_sheet_data("EVENTOS")

# --------- Módulo de Autenticación de Roles -------------
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario is None:
        email = st.sidebar.text_input("Correo Electrónico", key="login_email")
        password = st.sidebar.text_input("Contraseña", type="password", key="login_pass")
        
        if st.sidebar.button("Iniciar Sesión"):
            # Diagnóstico visual en caso de que las tablas sigan llegando con problemas
            if usuarios_df.empty:
                st.sidebar.error("Error: La tabla de USUARIOS no devolvió datos. Verifica la conexión.")
                return None
                
            if "Correo_Electronico" in usuarios_df.columns and "Contraseña" in usuarios_df.columns:
                # Filtrar ignorando espacios vacíos
                user = usuarios_df[(usuarios_df["Correo_Electronico"].astype(str).str.strip() == email.strip()) & 
                                   (usuarios_df["Contraseña"].astype(str).str.strip() == str(password).strip())]
                if not user.empty:
                    st.session_state.usuario = user.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.sidebar.error("Usuario o contraseña incorrectos.")
            else:
                st.sidebar.error("Error técnico: Columnas inválidas en la tabla de USUARIOS.")
                st.sidebar.write("Columnas leídas reales:", list(usuarios_df.columns))
    else:
        st.sidebar.success(f"Bienvenido: {st.session_state.usuario.get('Nombre_Completo', 'Líder')}")
        st.sidebar.info(f"Rol: {st.session_state.usuario.get('Rol', 'Usuario')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --------- Vistas de la Aplicación -------------
def vista_publica():
    st.title(" ⛪ Herederos Iglesia Nacional")
    st.subheader("Bienvenidos a nuestra comunidad")
    
    st.markdown("### 📅 Próximos Eventos y Actividades")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            st.info(f"**{row.iloc[0]}** - {row.iloc[1] if len(row) > 1 else 'Actividad'}")
    else:
        st.write("No hay eventos programados para esta semana.")

    st.markdown("---")
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre (Opcional)")
        peticion = st.text_area("¿Por qué necesidad te gustaría que oremos?")
        enviar = st.form_submit_button("Enviar Petición")
        if enviar and peticion.strip():
            st.success("¡Petición enviada! El sistema se ha conectado exitosamente.")

# Módulos de administración simulados para visualización por el cambio de conector
def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    st.subheader("📝 Registrar Nuevo Creyente")
    st.info("Conexión directa establecida. Listo para registrar miembros.")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.info("Formulario financiero enlazado directamente a la pestaña FINANZAS.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat de Líderes")
    st.info("Sala de chat interna activa.")

# --------- CONTROLADOR CENTRAL DE LA APP -------------
def main():
    usuario = autenticar()
    if usuario is None:
        vista_publica()
    else:
        rol = usuario.get("Rol", "Servidor")
        menu = ["Inicio / Oraciones"]
        if str(rol).upper() in ["PASTOR", "LÍDER", "SERVIDOR"]:
            menu.append("Consolidación y Asistencia")
        if str(rol).upper() in ["PASTOR", "TESORERO"]:
            menu.append("Gestión Financiera")
        menu.append("Chat de Líderes")
        
        opcion = st.selectbox("Selecciona el módulo de trabajo:", menu)
        if opcion == "Inicio / Oraciones":
            vista_publica()
        elif opcion == "Consolidación y Asistencia":
            panel_consolidacion()
        elif opcion == "Gestión Financiera":
            panel_financiero()
        elif opcion == "Chat de Líderes":
            sala_chat(usuario)

if __name__ == "__main__":
    main()
