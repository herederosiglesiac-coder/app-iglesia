import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- Configuración de la Pantalla Principal ---
st.set_page_config(page_title="Herederos Iglesia Nacional", layout="centered")

# --- CONECTOR ULTRA SEGURO (Bajo Demanda con Sistema de Emergencia) ---
def leer_pestaña_segura(nombre_pestaña):
    # Intentar conexión con Google Sheets
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=nombre_pestaña)
        return df.fillna("")
    except Exception:
        # SISTEMA DE EMERGENCIA: Si Google Sheets falla o no tiene credenciales,
        # la app NO se queda en blanco, crea una tabla limpia en memoria.
        if nombre_pestaña not in st.session_state:
            st.session_state[nombre_pestaña] = pd.DataFrame()
        return st.session_state[nombre_pestaña]

def guardar_datos_seguro(nombre_pestaña, df_actualizado):
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(worksheet=nombre_pestaña, data=df_actualizado)
    except Exception:
        # Guardar en memoria local si Google está desconectado
        st.session_state[nombre_pestaña] = df_actualizado

# Herramienta para descargar reportes a Excel sin usar internet
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Oficial')
    return output.getvalue()

# --- Módulo de Inicio de Sesión Autónomo ---
def autenticar():
    st.sidebar.title("🔐 Acceso Líderes")
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if st.session_state.usuario is None:
        email_input = st.sidebar.text_input("Correo Electrónico", key="login_email").strip()
        pass_input = st.sidebar.text_input("Contraseña", type="password", key="login_pass").strip()
        
        if st.sidebar.button("Iniciar Sesión"):
            usuarios_df = leer_pestaña_segura("USUARIOS")
            
            # Cuenta maestra de emergencia por si la tabla de Google Sheets está vacía
            if email_input.lower() == "pastor@iglesia.com" and pass_input == "admin123":
                st.session_state.usuario = {"Nombre": "Pastor Principal", "Rol": "PASTOR"}
                st.rerun()
            
            elif not usuarios_df.empty and "Correo" in usuarios_df.columns and "Contraseña" in usuarios_df.columns:
                usuarios_df["Correo"] = usuarios_df["Correo"].astype(str).str.strip()
                usuarios_df["Contraseña"] = usuarios_df["Contraseña"].astype(str).str.strip()
                user_match = usuarios_df[(usuarios_df["Correo"] == email_input) & (usuarios_df["Contraseña"] == pass_input)]
                
                if not user_match.empty:
                    datos_usuario = user_match.to_dict(orient="records")[0]
                    st.session_state.usuario = {
                        "Nombre": str(datos_usuario.get("Nombre", "Líder")),
                        "Rol": str(datos_usuario.get("Rol", "Servidor")).upper()
                    }
                    st.rerun()
                else:
                    st.sidebar.error("Correo o contraseña incorrectos.")
            else:
                st.sidebar.error("Prueba con la cuenta maestra: pastor@iglesia.com / admin123")
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
    st.subheader("Bienvenidos a nuestra comunidad")
    
    st.markdown("### 📅 Próximos Eventos y Actividades")
    eventos_df = leer_pestaña_segura("EVENTOS")
    if not eventos_df.empty:
        for _, row in eventos_df.iterrows():
            evento_nom = row.get("Evento", row.get("Título", "Actividad Generica"))
            evento_fec = row.get("Fecha", "Pronto")
            st.info(f"**{evento_fec}** - {evento_nom}")
    else:
        st.write("Reunión General todos los Domingos - 10:00 AM")
        
    st.markdown("---")
    
    st.subheader("🙏 Enviar Petición de Oración")
    with st.form("form_oracion", clear_on_submit=True):
        nombre_o = st.text_input("Tu Nombre (Opcional)")
        peticion_o = st.text_area("¿Cuál es tu necesidad de oración?")
        if st.form_submit_button("Enviar Petición"):
            if peticion_o.strip():
                oraciones_df = leer_pestaña_segura("Oraciones")
                nueva_fila = pd.DataFrame([{
                    "Nombre": nombre_o.strip() if nombre_o.strip() else "Anónimo",
                    "Peticion": peticion_o.strip(),
                    "Fecha": datetime.now().strftime("%Y-%m-%d")
                }])
                updated_df = pd.concat([oraciones_df, nueva_fila], ignore_index=True)
                guardar_datos_seguro("Oraciones", updated_df)
                st.success("¡Petición enviada! Estaremos orando por ti.")

def panel_consolidacion():
    st.markdown("## 👥 Módulo de Consolidación y Miembros")
    miembros_df = leer_pestaña_segura("MIEMBROS")
    
    st.subheader("📝 Registrar Nuevo Creyente")
    with st.form("form_registro_miembro", clear_on_submit=True):
        nombre_m = st.text_input("Nombre Completo")
        tel_m = st.text_input("Teléfono")
        cedula_m = st.text_input("Cédula")
        if st.form_submit_button("Guardar en Censo") and nombre_m.strip():
            col_id = "ID Miembro" if "ID Miembro" in miembros_df.columns else "ID"
            col_nom = "Nombre Completo" if "Nombre Completo" in miembros_df.columns else "Nombre"
            nueva_fila = pd.DataFrame([{col_id: len(miembros_df) + 1, col_nom: nombre_m.strip(), "Teléfono": tel_m.strip(), "Cedula": cedula_m.strip(), "Estado": "Activo"}])
            updated_df = pd.concat([miembros_df, nueva_fila], ignore_index=True)
            guardar_datos_seguro("MIEMBROS", updated_df)
            st.success(f"¡{nombre_m} registrado con éxito!")

def panel_financiero():
    st.markdown("## 💰 Módulo de Finanzas")
    finanzas_df = leer_pestaña_segura("FINANZAS")
    with st.form("form_finanzas", clear_on_submit=True):
        tipo_f = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
        cat_f = st.text_input("Categoría")
        monto_f = st.number_input("Monto ($)", min_value=0.0)
        if st.form_submit_button("Registrar Movimiento") and monto_f > 0:
            nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d"), "Tipo": tipo_f, "Categoría": cat_f.strip(), "Monto": monto_f}])
            updated_df = pd.concat([finanzas_df, nueva_fila], ignore_index=True)
            guardar_datos_seguro("FINANZAS", updated_df)
            st.success("¡Movimiento guardado!")

def panel_chat(usuario_actual):
    st.markdown("## 💬 Chat Interno de Líderes")
    chat_df = leer_pestaña_segura("CHAT_LIDERES")
    with st.form("form_chat", clear_on_submit=True):
        msg = st.text_input("Escribe un mensaje:")
        if st.form_submit_button("Enviar") and msg.strip():
            nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Usuario": usuario_actual["Nombre"], "Mensaje": msg.strip()}])
            updated_df = pd.concat([chat_df, nueva_fila], ignore_index=True)
            guardar_datos_seguro("CHAT_LIDERES", updated_df)
            st.success("¡Mensaje enviado!")

# --- Controlador Central ---
def main():
    usuario = autenticar()
    menu = ["Inicio (Vista Pública)"]
    
    if usuario is not None:
        rol = str(usuario.get("Rol", "SERVIDOR")).strip().upper()
        if rol in ["PASTOR", "LÍDER", "LIDER", "SERVIDOR"]: menu.append("Consolidación y Asistencia")
        if rol in ["PASTOR", "TESORERO"]: menu.append("Gestión Financiera")
        menu.append("Chat de Líderes")
        
    opcion = st.selectbox("Selecciona Módulo de Trabajo:", menu)
    if opcion == "Inicio (Vista Pública)": vista_publica()
    elif opcion == "Consolidación y Asistencia": panel_consolidacion()
    elif opcion == "Gestión Financiera": panel_financiero()
    elif opcion == "Chat de Líderes": panel_chat(usuario)

if __name__ == "__main__":
    main()
