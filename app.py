import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuración Base de la Pantalla ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- Base de Datos Interna de la App (Segura y 100% Libre de Bloqueos) ---
DB_MIEMBROS = "db_miembros.csv"
DB_ASISTENCIA = "db_asistencia.csv"
DB_FINANZAS = "db_finanzas.csv"
DB_EVENTOS = "db_eventos.csv"
DB_ORACIONES = "db_oraciones.csv"
DB_CHAT = "db_chat.csv"  # <- NUEVA BASE DE DATOS PARA EL CHAT INTERNO

# Funciones de utilidad para leer y escribir datos sin intermediarios
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo)
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

def guardar_datos(archivo, df):
    df.to_csv(archivo, index=False)

# --- Usuarios y Roles del Equipo ---
USUARIOS_LOCALES = [
    {"Nombre_Completo": "Jose Perez", "Correo_Electronico": "perezajosef@gmail.com", "Contraseña": "pastor123", "Rol": "PASTOR"}
]
usuarios_df = pd.DataFrame(USUARIOS_LOCALES)

# --- Módulo de Autenticación de Líderes ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state: st.session_state.usuario = None
    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip().lower()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        if st.sidebar.button("Iniciar Sesión"):
            user = usuarios_df[(usuarios_df["Correo_Electronico"] == email_input) & (usuarios_df["Contraseña"] == pass_input)]
            if not user.empty:
                st.session_state.usuario = {"Nombre": user.iloc[0]["Nombre_Completo"], "Rol": user.iloc[0]["Rol"]}
                st.rerun()
            else: st.sidebar.error("Correo o contraseña incorrectos.")
    else:
        st.sidebar.success(f"Hola: {st.session_state.usuario.get('Nombre')}")
        st.sidebar.info(f"Rol: {st.session_state.usuario.get('Rol')}")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.usuario = None
            st.rerun()
    return st.session_state.usuario

# --- 1. VISTA PÚBLICA (Eventos, Multimedia y Oraciones) ---
def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    
    # Sección de Eventos y Multimedia
    st.markdown("### 📅 Próximos Eventos y Actividades")
    df_e = cargar_datos(DB_EVENTOS, ["Fecha", "Título", "Tipo", "Enlace_Multimedia"])
    if not df_e.empty:
        for _, row in df_e.iterrows():
            with st.expander(f"🔹 {row['Fecha']} - {row['Título']} ({row['Tipo']})"):
                if pd.notna(row['Enlace_Multimedia']) and str(row['Enlace_Multimedia']).strip() != "":
                    st.video(row['Enlace_Multimedia']) if "youtube" in str(row['Enlace_Multimedia']) else st.link_button("🌐 Ver Transmisión / Material", row['Enlace_Multimedia'])
    else:
        st.info("Reunión General todos los Domingos - 10:00 AM")
        
    st.markdown("---")
    
    # Sección de Peticiones de Oración
    st.subheader("🙏 Enviar Petición de Oración")
    df_o = cargar_datos(DB_ORACIONES, ["Fecha", "Nombre", "Petición"])
    with st.form("form_oracion", clear_on_submit=True):
        nombre_o = st.text_input("Tu Nombre (Opcional)")
        peticion_o = st.text_area("¿Cuál es tu necesidad de oración?")
        if st.form_submit_button("Enviar Petición"):
            if peticion_o.strip():
                nueva_o = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Nombre": nombre_o.strip() or "Anónimo", "Petición": peticion_o.strip()}])
                df_o = pd.concat([df_o, nueva_o], ignore_index=True)
                guardar_datos(DB_ORACIONES, df_o)
                st.success("¡Petición guardada! Nuestro equipo de intercesores estará orando por ti.")
                st.rerun()

# --- 2. PANEL DE CONSOLIDACIÓN Y ASISTENCIA ---
def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación y Miembros")
    df_m = cargar_datos(DB_MIEMBROS, ["ID", "Nombre Completo", "Teléfono", "Cédula", "Estado"])
    
    st.subheader("📝 Registrar Nuevo Creyente")
    with st.form("form_registro_miembro", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo")
        tel_m = st.text_input("Número de Teléfono")
        cedula_m = st.text_input("Número de Cédula")
        estado_m = st.selectbox("Estado", ["Nuevo Convertido", "En Consolidación", "Miembro Activo"])
        if st.form_submit_button("Guardar Miembro") and nombre_m.strip():
            nueva_fila = pd.DataFrame([{"ID": len(df_m) + 1, "Nombre Completo": nombre_m.strip(), "Teléfono": tel_m.strip(), "Cédula": cedula_m.strip(), "Estado": estado_m}])
            df_m = pd.concat([df_m, nueva_fila], ignore_index=True)
            guardar_datos(DB_MIEMBROS, df_m)
            st.success(f"¡{nombre_m} registrado con éxito!")
            st.rerun()

    st.markdown("---")
    
    st.subheader("✔️ Control de Asistencia")
    if not df_m.empty:
        fecha_c = st.date_input("Fecha del Culto", datetime.now())
        presentes = st.multiselect("Selecciona los miembros presentes hoy:", df_m["Nombre Completo"].tolist())
        if st.button("Registrar Asistencia"):
            df_a = cargar_datos(DB_ASISTENCIA, ["Fecha", "Nombre Completo", "Asistió"])
            nuevos = pd.DataFrame([{"Fecha": fecha_c.strftime("%Y-%m-%d"), "Nombre Completo": p, "Asistió": "Sí"} for p in presentes])
            df_a = pd.concat([df_a, nuevos], ignore_index=True)
            guardar_datos(DB_ASISTENCIA, df_a)
            st.success("¡Asistencia del día guardada!")
    else:
        st.info("Registra miembros primero para poder pasar asistencia.")

    if not df_m.empty:
        st.markdown("### 📋 Lista General de la Congregación")
        st.dataframe(df_m, use_container_width=True)

# --- 3. PANEL GESTIÓN FINANCIERA ---
def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas (Ingresos y Egresos)")
    df_f = cargar_datos(DB_FINANZAS, ["Fecha", "Tipo", "Categoría", "Monto", "Sede", "Detalle"])
    
    with st.form("form_finanzas", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso (Diezmo/Ofrenda)", "Egreso (Gasto)"])
            cat_f = st.text_input("Categoría (Ej: Diezmo, Servicios, Eventos)")
            monto_f = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        with col2:
            sede_f = st.selectbox("Sede de la Iglesia", ["Sede Central", "Sede Norte", "Sede Sur"])
            detalle_f = st.text_area("Detalles / Concepto")
        
        if st.form_submit_button("Registrar Movimiento Financiero") and monto_f > 0:
            nuevo_mov = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Tipo": tipo_f, "Categoría": cat_f.strip(), "Monto": monto_f, "Sede": sede_f, "Detalle": detalle_f.strip()}])
            df_f = pd.concat([df_f, nuevo_mov], ignore_index=True)
            guardar_datos(DB_FINANZAS, df_f)
            st.success("¡Movimiento contable registrado de forma segura!")
            st.rerun()
            
    if not df_f.empty:
        st.markdown("### 📊 Historial Contable")
        st.dataframe(df_f, use_container_width=True)

# --- 4. PANEL DE EVENTOS Y MULTIMEDIA ---
def panel_eventos():
    st.markdown("## 🎬 Administración de Eventos y Multimedia")
    df_e = cargar_datos(DB_EVENTOS, ["Fecha", "Título", "Tipo", "Enlace_Multimedia"])
    
    with st.form("form_eventos", clear_on_submit=True):
        titulo_e = st.text_input("Título de la Actividad / Sermón")
        tipo_e = st.selectbox("Tipo de Recurso", ["Culto en Vivo", "Campamento", "Conferencia", "Material de Estudio"])
        url_e = st.text_input("Enlace de Video o Transmisión (YouTube, Facebook, Link público)")
        fecha_e = st.date_input("Fecha del Evento", datetime.now())
        
        if st.form_submit_button("Publicar en la Cartelera"):
            if titulo_e.strip():
                nuevo_e = pd.DataFrame([{"Fecha": fecha_e.strftime("%Y-%m-%d"), "Título": titulo_e.strip(), "Tipo": tipo_e, "Enlace_Multimedia": url_e.strip()}])
                df_e = pd.concat([df_e, nuevo_e], ignore_index=True)
                guardar_datos(DB_EVENTOS, df_e)
                st.success("¡Contenido publicado con éxito!")
                st.rerun()

# --- 5. PANEL CHAT INTERNO DE LÍDERES ---
def panel_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    df_c = cargar_datos(DB_CHAT, ["Fecha", "De", "Mensaje"])
    
    # Formulario para enviar mensaje al chat
    with st.form("form_enviar_chat", clear_on_submit=True):
        mensaje_c = st.text_input("Escribe un mensaje técnico o anuncio para el equipo:")
        if st.form_submit_button("Enviar al Muro") and mensaje_c.strip():
            nuevo_msg = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "De": usuario_actual["Nombre"], "Mensaje": mensaje_c.strip()}])
            df_c = pd.concat([df_c, nuevo_msg], ignore_index=True)
            guardar_datos(DB_CHAT, df_c)
            st.rerun()
            
    st.markdown("---")
    st.subheader("📋 Historial de Mensajes Recientes")
    if not df_c.empty:
        # Mostrar los mensajes organizados de forma visual amigable para celular
        for _, row in df_c.tail(20).iloc[::-1].iterrows():
            st.markdown(f"🔹 **{row['De']}** *({row['Fecha']})*")
            st.info(row['Mensaje'])
    else:
        st.caption("No hay mensajes registrados en la sala de chat.")

# --- Controlador de Navegación Central ---
def main():
    usuario = autenticar()
    if usuario is None:
        vista_publica()
    else:
        rol = str(usuario.get("Rol", "servidor")).strip().lower()
        menu = ["Inicio (Vista Pública)"]
