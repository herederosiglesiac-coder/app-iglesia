import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuración Base de la Pantalla ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- Bases de Datos Internas de la Aplicación ---
DB_MIEMBROS = "db_miembros.csv"
DB_ASISTENCIA = "db_asistencia.csv"
DB_FINANZAS = "db_finanzas.csv"
DB_CHAT = "db_chat.csv"  # <- Base de datos interna para el Chat

# Funciones de utilidad seguras para cargar y guardar información
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo)
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

def guardar_datos(archivo, df):
    df.to_csv(archivo, index=False)

# --- Base de Datos Local de Usuarios ---
# Copiado exactamente de tu código estable que sí funciona
USUARIOS_LOCALES = [
    {
        "Nombre_Completo": "Jose Perez",
        "Correo_Electronico": "perezajosef@gmail.com",
        "Contraseña": "pastor123",
        "Rol": "PASTOR"
    }
]
usuarios_df = pd.DataFrame(USUARIOS_LOCALES)

# --- Módulo de Autenticación de Líderes ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: 
        st.session_state.usuario = None
        
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip().lower()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            user = usuarios_df[(usuarios_df["Correo_Electronico"] == email_input) & (usuarios_df["Contraseña"] == pass_input)]
            
            if not user.empty:
                # --- ¡CORRECCIÓN CLAVE! Se extraen los datos usando el índice [0] seguro ---
                st.session_state.usuario = {
                    "Nombre": user.iloc[0]["Nombre_Completo"],
                    "Rol": user.iloc[0]["Rol"]
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
    
    # Cargar base de datos interna de miembros
    df_m = cargar_datos(DB_MIEMBROS, ["ID", "Nombre Completo", "Teléfono", "Cédula", "Estado"])
    
    # Formulario para capturar nuevos creyentes
    with st.form("form_registro_miembro", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo del Miembro")
        tel_m = st.text_input("Número de Teléfono")
        cedula_m = st.text_input("Número de Cédula")
        estado_m = st.selectbox("Estado de Consolidación", ["Nuevo Convertido", "En Consolidación", "Miembro Activo"])
        
        if st.form_submit_button("Guardar Miembro") and nombre_m.strip():
            nuevo_id = len(df_m) + 1
            nueva_fila = pd.DataFrame([{"ID": nuevo_id, "Nombre Completo": nombre_m.strip(), "Teléfono": tel_m.strip(), "Cédula": cedula_m.strip(), "Estado": estado_m}])
            df_m = pd.concat([df_m, nueva_fila], ignore_index=True)
            guardar_datos(DB_MIEMBROS, df_m)
            st.success(f"¡{nombre_m} registrado exitosamente!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("📋 Miembros Registrados Recientemente")
    if not df_m.empty:
        st.dataframe(df_m, use_container_width=True)
    else:
        st.caption("No hay miembros registrados aún.")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    st.success("Panel financiero activo. Control de ingresos y egresos.")
    
    # Cargar base de datos interna contable
    df_f = cargar_datos(DB_FINANZAS, ["Fecha", "Tipo", "Monto", "Sede", "Detalle"])
    
    with st.form("form_registro_finanzas", clear_on_submit=True):
        tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso (Diezmo / Ofrenda)", "Egreso (Gasto)"])
        monto_f = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        sede_f = st.selectbox("Sede", ["Sede Central", "Sedes Locales"])
        detalle_f = st.text_area("Concepto / Detalle")
        
        if st.form_submit_button("Registrar Movimiento") and monto_f > 0:
            nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Tipo": tipo_f, "Monto": monto_f, "Sede": sede_f, "Detalle": detalle_f.strip()}])
            df_f = pd.concat([df_f, nueva_fila], ignore_index=True)
            guardar_datos(DB_FINANZAS, df_f)
            st.success("¡Movimiento contable registrado con éxito!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("📊 Historial Contable Reciente")
    if not df_f.empty:
        st.dataframe(df_f, use_container_width=True)
    else:
        st.caption("No hay movimientos contables registrados hoy.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    st.success("Muro de mensajes activo para coordinación técnica.")
    
    # Cargar historial del chat interno
    df_c = cargar_datos(DB_CHAT, ["Fecha", "De", "Mensaje"])
    
    with st.form("form_enviar_chat", clear_on_submit=True):
        mensaje_c = st.text_input("Escribe un mensaje para el equipo:")
        if st.form_submit_button("Enviar al Muro") and mensaje_c.strip():
            nuevo_msg = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "De": usuario_actual["Nombre"], "Mensaje": mensaje_c.strip()}])
            df_c = pd.concat([df_c, nuevo_msg], ignore_index=True)
            guardar_datos(DB_CHAT, df_c)
            st.rerun()
            
    st.markdown("---")
    if not df_c.empty:
        # Mostrar los últimos 15 mensajes en orden cronológico inverso (el más nuevo arriba)
        for _, row in df_c.tail(15).iloc[::-1].iterrows():
            st.markdown(f"🔹 **{row['De']}** *({row['Fecha']})*")
            st.info(row['Mensaje'])
    else:
        st.caption("No hay mensajes en la sala de chat de líderes.")

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
