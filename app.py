import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página para dispositivos móviles
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# Inicializar la conexión oficial de Streamlit con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --------- Carga de Datos Eficiente -------------
@st.cache_data(ttl=60)  # Actualiza los datos automáticamente cada minuto
def load_sheet_data(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name)
    except Exception:
        return pd.DataFrame()

# Cargar todas las fuentes de datos exactas de tus pestañas
usuarios_df = load_sheet_data("USUARIOS")
miembros_df = load_sheet_data("MIEMBROS")
asistencia_df = load_sheet_data("ASISTENCIA")
oraciones_df = load_sheet_data("Oraciones")  # <- CORREGIDO: 'Oraciones' tal como tu pestaña
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
            if not usuarios_df.empty and "Correo_Electronico" in usuarios_df.columns and "Contraseña" in usuarios_df.columns:
                user = usuarios_df[(usuarios_df["Correo_Electronico"] == email) & (usuarios_df["Contraseña"] == str(password))]
                if not user.empty:
                    st.session_state.usuario = user.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.sidebar.error("Usuario o contraseña incorrectos.")
            else:
                st.sidebar.error("Error técnico: Verifica las columnas de la tabla de USUARIOS.")
    else:
        st.sidebar.success(f"Bienvenido: {st.session_state.usuario['Nombre']}")
        st.sidebar.info(f"Rol: {st.session_state.usuario['Rol']}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --------- Vistas de la Aplicación -------------
def vista_publica():
    st.title(" ⛪ Herederos Iglesia Nacional")
    st.subheader("Bienvenidos a nuestra comunidad")
    
    # Anuncios / Eventos
    st.markdown("### 📅 Próximos Eventos y Actividades")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            st.info(f"**{row.get('Fecha', 'Pronto')}** - {row.get('Evento', 'Reunión General')}")
    else:
        st.write("No hay eventos programados para esta semana.")

    st.markdown("---")
    # Formulario Público de Oración (Pestaña 'Oraciones')
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre (Opcional)")
        peticion = st.text_area("¿Por qué necesidad te gustaría que oremos?")
        enviar = st.form_submit_button("Enviar Petición")
        
        if enviar and peticion.strip():
            nueva_fila = pd.DataFrame([{
                "Nombre": nombre if nombre else "Anónimo",
                "Peticion": peticion,
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }])
            updated_df = pd.concat([oraciones_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="Oraciones", data=updated_df)  # <- CORREGIDO: Guarda en 'Oraciones'
            st.success("¡Petición enviada! Nuestra red de intercesores estará orando por ti.")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación")
    
    # 1. Registrar Nuevo Miembro
    st.subheader("📝 Registrar Nuevo Creyente")
    with st.form("form_miembros", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_m = st.text_input("Nombre Completo")
            tel_m = st.text_input("Teléfono")
        with col2:
            correo_m = st.text_input("Correo")
            cedula_m = st.text_input("Cédula")
        dir_m = st.text_input("Dirección")
        
        agregar = st.form_submit_button("Guardar en base de datos")
        if agregar and nombre_m.strip():
            nueva_fila = pd.DataFrame([{
                "ID Miembro": len(miembros_df) + 1,
                "Nombre Completo": nombre_m,
                "Teléfono": tel_m,
                "Correo": correo_m,
                "Dirección": dir_m,
                "Cedula": cedula_m,
                "Estado": "Miembro Activo",
                "Estatus de Consolidación": "Consolidado"
            }])
            updated_df = pd.concat([miembros_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="MIEMBROS", data=updated_df)
            st.success(f"¡{nombre_m} registrado exitosamente!")

    st.markdown("---")
    # 2. Pase de Asistencia
    st.subheader("✔️ Control de Asistencia")
    if not miembros_df.empty:
        fecha_culto = st.date_input("Fecha del Servicio/Culto", datetime.now())
        # Buscamos la columna exacta de tu Google Sheet 'Nombre Completo'
        col_nombre = "Nombre Completo" if "Nombre Completo" in miembros_df.columns else miembros_df.columns[1]
        lista_nombres = miembros_df[col_nombre].dropna().tolist()
        asistieron = st.multiselect("Selecciona los miembros presentes:", lista_nombres)
        
        if st.button("Registrar Lista de Asistencia"):
            nuevos_registros = []
            for nombre in asistieron:
                nuevos_registros.append({
                    "Fecha": fecha_culto.strftime("%Y-%m-%d"),
                    "Nombre Completo": nombre,
                    "Asistió": "Sí"
                })
            if nuevos_registros:
                nuevas_filas_df = pd.DataFrame(nuevos_registros)
                updated_df = pd.concat([asistencia_df, nuevas_filas_df], ignore_index=True)
                conn.update(worksheet="ASISTENCIA", data=updated_df)
                st.success("¡Asistencia guardada correctamente!")
    else:
        st.info("No hay miembros registrados para pasar asistencia.")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    with st.form("form_finanzas", clear_on_submit=True):
        fecha_f = st.date_input("Fecha de Registro", datetime.now())
        tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
        cat_f = st.text_input("Categoría (Ej: Diezmo, Ofrenda, Servicio Público)")
        det_f = st.text_area("Detalle / Concepto")
        monto_f = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        sede_f = st.selectbox("Sede", ["Central", "Sedes Locales"])
        
        guardar_f = st.form_submit_button("Registrar en Finanzas")
        if guardar_f and monto_f > 0:
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha_f.strftime("%Y-%m-%d"),
                "Tipo": tipo_f,
                "Categoría": cat_f,
                "Detalle": det_f,
                "Monto": monto_f,
                "Sede": sede_f
            }])
            updated_df = pd.concat([finanzas_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="FINANZAS", data=updated_df)
            st.success("Movimiento financiero registrado de forma segura.")

def sala_chat(usuario_actual):
    st.markdown("## 💬 Chat de Líderes")
    with st.form("form_chat", clear_on_submit=True):
        msg = st.text_input("Escribe un mensaje importante para el equipo:")
        enviar_msg = st.form_submit_button("Enviar al Muro")
        
        if enviar_msg and msg.strip():
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Usuario": usuario_actual.get("Nombre", "Líder"),
                "Mensaje": msg
            }])
            updated_df = pd.concat([chat_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="CHAT_LIDERES", data=updated_df)
            st.rerun()
            
    st.markdown("### 📋 Mensajes Recientes")
    if not chat_df.empty:
        for _, row in chat_df.tail(15).iloc[::-1].iterrows():
            st.write(f"🔹 **{row.get('Usuario', 'Líder')}** ({row.get('Fecha', '')}): {row.get('Mensaje', '')}")
    else:
        st.caption("No hay mensajes internos registrados.")

# --------- CONTROLADOR CENTRAL DE LA APP -------------
def main():
    usuario = autenticar()
    
    if usuario is None:
        vista_publica()
    else:
        rol = usuario.get("Rol", "Servidor")
        
        menu = ["Inicio / Oraciones"]
        if rol in ["Pastor", "Líder", "Servidor"]:
            menu.append("Consolidación y Asistencia")
        if rol in ["Pastor", "Tesorero"]:
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
