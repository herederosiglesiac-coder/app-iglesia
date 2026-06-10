import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURACIÓN ---
SUPABASE_URL = "https://oxokuijiqeykidmvwbtu.supabase.co"
SUPABASE_KEY = "sb_publishable_5L7tNIMWPXaWjeoLvniUEQ_Llbhtb1K"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar(tabla, datos):
    try:
        supabase.table(tabla).insert(datos).execute()
        st.success(f"¡Registro exitoso en {tabla}!")
    except Exception as e: st.error(f"Error en {tabla}: {e}")

st.title("👑 HEREDEROS IGLESIA")

# --- NAVEGACIÓN ---
opciones = ["🏠 Inicio", "📺 Sermones", "📅 Eventos", "🙏 Oración", "🔐 Acceso Servidores"]
if st.session_state.get('autenticado'):
    opciones = ["🏠 Panel", "👥 Consolidación", "✅ Asistencia", "💰 Finanzas", "📺 Sermones", "📅 Eventos", "🙏 Oración", "💬 Chat", "🚪 Salir"]

menu = st.sidebar.selectbox("Menú Principal", opciones)

# --- 1. CONSOLIDACIÓN (Tabla: miembros) ---
if menu == "👥 Consolidación":
    with st.form("form_miembros"):
        datos = {
            "nombre_completo": st.text_input("Nombre Completo"),
            "cedula": st.text_input("Cédula"),
            "telefono": st.text_input("Teléfono"),
            "correo": st.text_input("Correo"),
            "fecha_nacimiento": str(st.date_input("Fecha Nacimiento")),
            "estado": st.selectbox("Estado", ["Nuevo", "Activo", "Inactivo"]),
            "estatus_consolidacion": st.selectbox("Estatus Consolidación", ["En proceso", "Consolidado"]),
            "consolidador_asignado": st.text_input("Consolidador"),
            "ministerios": st.text_input("Ministerios"),
            "sede": st.text_input("Sede"),
            "direccion": st.text_area("Dirección"),
            "notas_seguimiento": st.text_area("Notas")
        }
        if st.form_submit_button("Guardar Miembro"): guardar("miembros", datos)

# --- 2. FINANZAS (Tabla: transaccion) ---
elif menu == "💰 Finanzas":
    with st.form("form_transaccion"):
        datos = {
            "fecha": str(st.date_input("Fecha")),
            "tipo_movimiento": st.selectbox("Tipo", ["Ingreso", "Egreso"]),
            "categoria": st.selectbox("Categoría", ["Diezmo", "Ofrenda", "Evento", "Servicios"]),
            "monto": float(st.number_input("Monto")),
            "metodo_pago": st.selectbox("Método", ["Efectivo", "Transferencia", "Pago Móvil"]),
            "estatus_deposito": st.selectbox("Estatus", ["Pendiente", "Completado"]),
            "sede": st.text_input("Sede"),
            "comprobante_url": st.text_input("URL Comprobante"),
            "descripcion": st.text_area("Descripción")
        }
        if st.form_submit_button("Registrar Transacción"): guardar("transaccion", datos)

# --- 3. ASISTENCIA (Tabla: asistencia) ---
elif menu == "✅ Asistencia":
    with st.form("form_asistencia"):
        datos = {
            "fecha": str(st.date_input("Fecha")),
            "tipo_servicio": st.selectbox("Servicio", ["Dominical", "Ayuno", "Liderazgo"]),
            "sede": st.text_input("Sede"),
            "cantidad_asistentes": int(st.number_input("Cantidad", min_value=0)),
            "observaciones": st.text_area("Observaciones")
        }
        if st.form_submit_button("Registrar Asistencia"): guardar("asistencia", datos)

# --- 4. SERMONES (Tabla: sermones) ---
elif menu == "📺 Sermones":
    with st.form("form_sermones"):
        datos = {
            "titulo": st.text_input("Título"),
            "predicador": st.text_input("Predicador"),
            "link_video": st.text_input("Link (YouTube/IG)"),
            "fecha": str(st.date_input("Fecha"))
        }
        if st.form_submit_button("Guardar Sermón"): guardar("sermones", datos)

# --- 5. EVENTOS (Tabla: eventos) ---
elif menu == "📅 Eventos":
    with st.form("form_eventos"):
        datos = {
            "nombre_evento": st.text_input("Nombre Evento"),
            "fecha_hora": str(st.date_input("Fecha")),
            "sede": st.text_input("Sede"),
            "descripcion": st.text_area("Descripción")
        }
        if st.form_submit_button("Registrar Evento"): guardar("eventos", datos)

# --- 6. ORACIÓN Y CHAT ---
elif menu == "🙏 Oración":
    with st.form("form_oracion"):
        datos = {"nombre": st.text_input("Nombre"), "telefono": st.text_input("Teléfono"), "sede": st.text_input("Sede"), "peticion": st.text_area("Petición")}
        if st.form_submit_button("Enviar"): guardar("oraciones", datos)

elif menu == "💬 Chat":
    with st.form("form_chat"):
        datos = {"autor": st.session_state.get("usuario_nombre", "Líder"), "mensaje": st.text_input("Mensaje")}
        if st.form_submit_button("Enviar"): guardar("chat_lideres", datos)
