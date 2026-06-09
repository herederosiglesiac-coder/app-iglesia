import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- Configuración Visual Móvil ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- Conexión Segura con tu Google Sheet ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión con el servidor de Google: {e}")
    st.stop()

# Función limpia para cargar datos de tus pestañas reales
def leer_pestaña(nombre_pestaña):
    try:
        df = conn.read(worksheet=nombre_pestaña)
        return df.fillna("")
    except Exception:
        # Si la pestaña no tiene datos, crea una estructura básica para evitar pantallas en blanco
        return pd.DataFrame()

# Cargar las tablas que me mostraste en la imagen
usuarios_df = leer_pestaña("USUARIOS")
miembros_df = leer_pestaña("MIEMBROS")
asistencia_df = leer_pestaña("ASISTENCIA")
oraciones_df = leer_pestaña("Oraciones")  # Respeta tu mayúscula inicial 'Oraciones'
finanzas_df = leer_pestaña("FINANZAS")
chat_df = leer_pestaña("CHAT_LIDERES")
eventos_df = leer_pestaña("EVENTOS")

# Función técnica para transformar tablas de la iglesia en archivos descargables Excel
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Oficial')
    return output.getvalue()

# --- Módulo de Inicio de Sesión por Roles ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            if not usuarios_df.empty and "Correo" in usuarios_df.columns and "Contraseña" in usuarios_df.columns:
                # Filtrado seguro convirtiendo a texto
                usuarios_df["Correo"] = usuarios_df["Correo"].astype(str).str.strip()
                usuarios_df["Contraseña"] = usuarios_df["Contraseña"].astype(str).str.strip()
                
                user_match = usuarios_df[(usuarios_df["Correo"] == email_input) & (usuarios_df["Contraseña"] == pass_input)]
                
                if not user_match.empty:
                    st.session_state.usuario = {
                        "Nombre": str(user_match.iloc[0].get("Nombre", "Líder")),
                        "Rol": str(user_match.iloc[0].get("Rol", "Servidor")).upper()
                    }
                    st.rerun()
                else:
                    st.sidebar.error("Correo o contraseña incorrectos.")
            else:
                st.sidebar.warning("Tabla 'USUARIOS' no disponible o sin columnas 'Correo'/'Contraseña'.")
    else:
        st.sidebar.success(f"Hola: {st.session_state.usuario.get('Nombre')}")
        st.sidebar.info(f"Rol: {st.session_state.usuario.get('Rol')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --- 1. VISTA PÚBLICA (Anuncios de la Iglesia y Oraciones) ---
def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    st.subheader("Bienvenidos a nuestra comunidad")
    
    # Cartelera de Eventos
    st.markdown("### 📅 Próximos Eventos y Actividades")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            evento_nom = row.get("Evento", row.get("Título", "Actividad"))
            evento_fec = row.get("Fecha", "Pronto")
            st.info(f"**{evento_fec}** - {evento_nom}")
    else:
        st.write("Reunión General todos los Domingos - 10:00 AM")
        
    st.markdown("---")
    
    # Formulario Abierto de Oración (Pestaña 'Oraciones')
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre_o = st.text_input("Tu Nombre (Opcional)")
        peticion_o = st.text_area("¿Cuál es tu necesidad de oración?")
        if st.form_submit_button("Enviar Petición"):
            if peticion_o.strip():
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre_o.strip() if nombre_o.strip() else "Anónimo",
                    "Peticion": peticion_o.strip(),
                    "Fecha": datetime.now().strftime("%Y-%m-%d")
                }])
                updated_df = pd.concat([oraciones_df, nueva_fila], ignore_index=True)
                conn.update(worksheet="Oraciones", data=updated_df)
                st.success("¡Petición enviada! Estaremos orando por ti.")
                st.rerun()

# --- 2. PANEL DE CONSOLIDACIÓN Y ASISTENCIA ---
def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación y Miembros")
    
    # Registrar miembro en la pestaña 'MIEMBROS'
    st.subheader("📝 Registrar Nuevo Creyente")
    with st.form("form_registro_miembro", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo")
        tel_m = st.text_input("Teléfono")
        cedula_m = st.text_input("Cédula")
        if st.form_submit_button("Guardar en Censo") and nombre_m.strip():
            col_id = "ID Miembro" if "ID Miembro" in miembros_df.columns else "ID"
            col_nom = "Nombre Completo" if "Nombre Completo" in miembros_df.columns else "Nombre"
            
            nueva_fila = pd.DataFrame([{
                col_id: len(miembros_df) + 1,
                col_nom: nombre_m.strip(),
                "Teléfono": tel_m.strip(),
                "Cedula": cedula_m.strip(),
                "Estado": "Activo"
            }])
            updated_df = pd.concat([miembros_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="MIEMBROS", data=updated_df)
            st.success(f"¡{nombre_m} registrado con éxito!")
            st.rerun()

    st.markdown("---")
    
    # Control de Asistencia Semanal (Pestaña 'ASISTENCIA')
    st.subheader("✔️ Control de Asistencia")
    col_nom_m = "Nombre Completo" if "Nombre Completo" in miembros_df.columns else "Nombre"
    if not miembros_df.empty and col_nom_m in miembros_df.columns:
        fecha_c = st.date_input("Fecha del Servicio/Culto", datetime.now())
        presentes = st.multiselect("Miembros presentes hoy:", miembros_df[col_nom_m].dropna().tolist())
        if st.button("Guardar Lista de Asistencia"):
            col_asist_nom = "Nombre Completo" if "Nombre Completo" in asistencia_df.columns else "Nombre"
            nuevos_registros = pd.DataFrame([{
                "Fecha": fecha_c.strftime("%Y-%m-%d"),
                col_asist_nom: p,
                "Asistió": "Sí"
            } for p in presentes])
            updated_df = pd.concat([asistencia_df, nuevos_registros], ignore_index=True)
            conn.update(worksheet="ASISTENCIA", data=updated_df)
            st.success("¡Asistencia guardada!")
            st.rerun()
            
    st.markdown("---")
    if not miembros_df.empty:
        st.dataframe(miembros_df, use_container_width=True)
        excel_data = convertir_a_excel(miembros_df)
        st.download_button(label="📥 Descargar Base de Miembros (Excel)", data=excel_data, file_name="Censo_Miembros.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- 3. PANEL GESTIÓN FINANCIERA (Pestaña 'FINANZAS') ---
def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas (Ingresos y Egresos)")
    with st.form("form_finanzas", clear_on_submit=True):
        tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
        cat_f = st.text_input("Categoría (Ej: Diezmo, Ofrenda, Luz, Misiones)")
        monto_f = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        sede_f = st.selectbox("Sede de la Iglesia", ["Sede Central", "Sede Norte", "Sede Sur", "Sede Este"])
        detalle_f = st.text_area("Detalle / Concepto")
        
        if st.form_submit_button("Registrar Movimiento") and monto_f > 0:
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Tipo": tipo_f,
                "Categoría": cat_f.strip(),
                "Monto": monto_f,
                "Sede": sede_f,
                "Detalle": detalle_f.strip()
            }])
            updated_df = pd.concat([finanzas_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="FINANZAS", data=updated_df)
            st.success("¡Movimiento financiero guardado!")
            st.rerun()
            
    st.markdown("---")
    if not finanzas_df.empty:
        st.dataframe(finanzas_df, use_container_width=True)
        excel_finanzas = convertir_a_excel(finanzas_df)
        st.download_button(label="📥 Descargar Reporte Financiero (Excel)", data=excel_finanzas, file_name="Libro_Finanzas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- 4. PANEL CHAT INTERNO DE LÍDERES (Pestaña 'CHAT_LIDERES') ---
def panel_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    with st.form("form_chat", clear_on_submit=True):
        msg = st.text_input("Escribe un mensaje para el equipo:")
        if st.form_submit_button("Enviar al Muro") and msg.strip():
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Usuario": usuario_actual["Nombre"],
                "Mensaje": msg.strip()
            }])
            updated_df = pd.concat([chat_df, nueva_fila], ignore_index=True)
            conn.update(worksheet="CHAT_LIDERES", data=updated_df)
            st.rerun()
            
    st.markdown("---")
    if not chat_df.empty:
        for _, row in chat_df.tail(15).iloc[::-1].iterrows():

