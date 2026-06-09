import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

# --- Configuración Base de la Pantalla ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- Base de Datos Interna de la App (Segura y Autónoma) ---
DB_MIEMBROS = "db_miembros.csv"
DB_ASISTENCIA = "db_asistencia.csv"
DB_FINANZAS = "db_finanzas.csv"
DB_EVENTOS = "db_eventos.csv"
DB_ORACIONES = "db_oraciones.csv"
DB_CHAT = "db_chat.csv"

# Funciones de utilidad para leer y escribir datos de forma segura
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            return df.fillna("")
        except:
            return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

def guardar_datos(archivo, df):
    df.to_csv(archivo, index=False)

# Función técnica para transformar tablas en archivos descargables de Excel
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Oficial')
    return output.getvalue()

# --- Base de Datos Local de Usuarios Autorizados ---
USUARIOS_LOCALES = [
    {"Nombre_Completo": "Jose Perez", "Correo_Electronico": "perezajosef@gmail.com", "Contrasena": "pastor123", "Rol": "PASTOR"}
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
            # Búsqueda nativa y segura en el diccionario de datos
            usuario_encontrado = None
            for u in USUARIOS_LOCALES:
                if u["Correo_Electronico"] == email_input and u["Contrasena"] == pass_input:
                    usuario_encontrado = u
                    break
            
            if usuario_encontrado:
                st.session_state.usuario = {
                    "Nombre": usuario_encontrado["Nombre_Completo"],
                    "Rol": usuario_encontrado["Rol"]
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

# --- 1. VISTA PÚBLICA (Eventos, Transmisiones y Oraciones) ---
def vista_publica():
    st.title("⛪ Herederos Iglesia Nacional")
    
    # Cartelera Dinámica de Eventos y Videos de YouTube
    st.markdown("### 📅 Cartelera Digital y Transmisiones")
    df_e = cargar_datos(DB_EVENTOS, ["Fecha", "Título", "Tipo", "Enlace_Multimedia"])
    if not df_e.empty:
        for _, row in df_e.iterrows():
            with st.expander(f"🔹 {row['Fecha']} - {row['Título']} ({row['Tipo']})"):
                st.write("Recurso disponible para la congregación:")
                url_m = str(row['Enlace_Multimedia']).strip()
                if url_m and url_m != "nan" and url_m != "":
                    if "youtube.com" in url_m or "youtu.be" in url_m:
                        st.video(url_m)
                    else:
                        st.link_button("🌐 Abrir Enlace Externo / Material", url_m)
                else:
                    st.caption("Este evento no incluye material multimedia.")
    else:
        st.info("Reunión General todos los Domingos - 10:00 AM")
        
    st.markdown("---")
    
    # Buzón Público de Peticiones de Oración
    st.subheader("🙏 Enviar Petición de Oración")
    df_o = cargar_datos(DB_ORACIONES, ["Fecha", "Nombre", "Petición"])
    with st.form("form_oracion", clear_on_submit=True):
        nombre_o = st.text_input("Tu Nombre (Opcional)")
        peticion_o = st.text_area("¿Cuál es tu necesidad o motivo de oración?")
        if st.form_submit_button("Enviar Petición al Equipo"):
            if peticion_o.strip():
                nueva_o = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Nombre": nombre_o.strip() or "Anónimo", "Petición": peticion_o.strip()}])
                df_o = pd.concat([df_o, nueva_o], ignore_index=True)
                guardar_datos(DB_ORACIONES, df_o)
                st.success("¡Petición guardada! Nuestro equipo de líderes estará intercediendo por ti.")
                st.rerun()

# --- 2. PANEL DE CONSOLIDACIÓN Y ASISTENCIA ---
def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación y Miembros")
    df_m = cargar_datos(DB_MIEMBROS, ["ID", "Nombre Completo", "Teléfono", "Cédula", "Estado"])
    
    # Formulario de Miembros
    st.subheader("📝 Registrar Nuevo Creyente")
    with st.form("form_registro_miembro", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo")
        tel_m = st.text_input("Número de Teléfono")
        cedula_m = st.text_input("Número de Cédula")
        estado_m = st.selectbox("Estado actual", ["Nuevo Convertido", "En Consolidación", "Miembro Activo"])
        if st.form_submit_button("Guardar en Censo") and nombre_m.strip():
            nueva_fila = pd.DataFrame([{"ID": len(df_m) + 1, "Nombre Completo": nombre_m.strip(), "Teléfono": tel_m.strip(), "Cédula": cedula_m.strip(), "Estado": estado_m}])
            df_m = pd.concat([df_m, nueva_fila], ignore_index=True)
            guardar_datos(DB_MIEMBROS, df_m)
            st.success(f"¡{nombre_m} registrado exitosamente!")
            st.rerun()

    st.markdown("---")
    
    # Control de Asistencia Semanal
    st.subheader("✔️ Control de Asistencia")
    if not df_m.empty:
        fecha_c = st.date_input("Fecha del Servicio/Culto", datetime.now())
        presentes = st.multiselect("Selecciona los miembros presentes hoy:", df_m["Nombre Completo"].tolist())
        if st.button("Guardar Lista de Asistencia"):
            df_a = cargar_datos(DB_ASISTENCIA, ["Fecha", "Nombre Completo", "Asistió"])
            nuevos = pd.DataFrame([{"Fecha": fecha_c.strftime("%Y-%m-%d"), "Nombre Completo": p, "Asistió": "Sí"} for p in presentes])
            df_a = pd.concat([df_a, nuevos], ignore_index=True)
            guardar_datos(DB_ASISTENCIA, df_a)
            st.success("¡Asistencia del día guardada exitosamente!")
    else:
        st.info("Registra miembros arriba para poder pasar asistencia.")

    st.markdown("---")
    st.subheader("📋 Lista General de la Congregación")
    if not df_m.empty:
        st.dataframe(df_m, use_container_width=True)
        excel_data = convertir_a_excel(df_m)
        st.download_button(label="📥 Descargar Base de Miembros (Excel)", data=excel_data, file_name=f"Censo_Miembros_{datetime.now().strftime('%Y-%m-%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.caption("No hay miembros registrados aún.")

# --- 3. PANEL GESTIÓN FINANCIERA ---
def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas (Ingresos y Egresos)")
    df_f = cargar_datos(DB_FINANZAS, ["Fecha", "Tipo", "Categoría", "Monto", "Sede", "Detalle"])
    
    # Formulario Contable
    with st.form("form_finanzas", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso (Diezmo/Ofrenda)", "Egreso (Gasto)"])
            cat_f = st.text_input("Categoría (Ej: Diezmos, Ofrendas, Luz, Eventos, Misiones)")
            monto_f = st.number_input("Monto ($)", min_value=0.0, step=1.0)
        with col2:
            sede_f = st.selectbox("Sede de la Iglesia", ["Sede Central", "Sede Norte", "Sede Sur", "Sede Este"])
            detalle_f = st.text_area("Concepto / Descripción del movimiento")
        
        if st.form_submit_button("Registrar en Libros Contables") and monto_f > 0:
            nuevo_mov = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Tipo": tipo_f, "Categoría": cat_f.strip(), "Monto": monto_f, "Sede": sede_f, "Detalle": detalle_f.strip()}])
            df_f = pd.concat([df_f, nuevo_mov], ignore_index=True)
            guardar_datos(DB_FINANZAS, df_f)
            st.success("¡Movimiento financiero archivado correctamente!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("📊 Historial Contable")
    if not df_f.empty:
        st.dataframe(df_f, use_container_width=True)
        excel_finanzas = convertir_a_excel(df_f)
        st.download_button(label="📥 Descargar Reporte Financiero (Excel)", data=excel_finanzas, file_name=f"Libro_Finanzas_{datetime.now().strftime('%Y-%m-%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.caption("No hay registros contables en los libros de la aplicación.")

# --- 4. PANEL DE PUBLICACIÓN DE EVENTOS Y MULTIMEDIA ---
def panel_eventos():
    st.markdown("## 🎬 Administración de Eventos y Multimedia")
    st.write("Desde aquí controlas los videos y anuncios que ve la congregación al abrir la aplicación.")
    df_e = cargar_datos(DB_EVENTOS, ["Fecha", "Título", "Tipo", "Enlace_Multimedia"])
    
    with st.form("form_eventos", clear_on_submit=True):
        titulo_e = st.text_input("Título de la Actividad / Nombre del Sermón")
        tipo_e = st.selectbox("Tipo de Recurso", ["Culto en Vivo", "Campamento", "Conferencia", "Material de Estudio", "Anuncio de la Semana"])
        url_e = st.text_input("Enlace de Video o Transmisión (Pega el link de YouTube o Facebook)")
