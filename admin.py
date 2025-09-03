import flet as ft
from supabase_client import supa
import asyncio
from flet import TextOverflow
import threading
from datetime import datetime
import time
import tempfile
import openpyxl
from openpyxl.styles import Font
from flet import ScrollMode
import base64

def admin_login(page: ft.Page):
    email_input = ft.TextField(
        hint_text="Correo",
        width=300,
        height= 50,       # aquí ajusta a la altura que quieras
        border_radius=6,
        keyboard_type=ft.KeyboardType.TEXT,
        text_style=ft.TextStyle(color="#090909", size=12),
        bgcolor="#FFFFFF",
        focused_border_color="#ff2626"
    )
    password_input = ft.TextField(
        hint_text="Contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        height= 50,       # aquí ajusta a la altura que quieras
        border_radius=6,
        keyboard_type=ft.KeyboardType.TEXT,
        text_style=ft.TextStyle(color="#090909", size=12),
        bgcolor="#FFFFFF",
        focused_border_color="#ff2626"
    )
    mensaje = ft.Text(color="red")

    def autenticar(e):
        try:
            auth_response = supa.auth.sign_in_with_password({
                "email": email_input.value,
                "password": password_input.value
            })
            if auth_response.user:
                cargar_panel_admin(page)
        except Exception as err:
            mensaje.value = "Credenciales inválidas"
            page.update()

    logo = ft.Image(
            src="solo_logo.png",
            width=100,
            height=74,
            fit=ft.ImageFit.CONTAIN
        )

    boton_login = ft.Container(
        content= ft.ElevatedButton(
            content=ft.Text(
                "Entrar",
                size=12,
                color="#000000",
                style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)
            ),
            bgcolor="#fddd58",
            on_click=autenticar
        ),
        width= 250
    )

    layout = ft.Column([
        logo,
        ft.Text("Panel Administrativo", size=20, weight="bold"),
        email_input,
        password_input,
        boton_login,
        mensaje,
    ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.controls.clear()
    page.add(
        ft.Container(
            content=layout,
            alignment=ft.alignment.center,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#000000","#101010","#1e1e1e","#343434","#404040","#292929","#121212"]
            )
        )
    )
    page.update()

def cargar_panel_admin(page: ft.Page):
    def abrir_configuracion(e):
        mostrar_configuracion(page)

    def abrir_ordenes(e):
        mostrar_ordenes(page)

    def ver_resumen_cartones(e):
        mostrar_resumen_cartones(page)

    logo = ft.Image(
        src="solo_logo.png",
        width=100,
        height=74,
        fit=ft.ImageFit.CONTAIN
    )

    boton_config = ft.Container(
        content= ft.ElevatedButton(
            content=ft.Text(
                "Configuración",
                size=12,
                color="#000000",
                style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)
            ),
            bgcolor="#fddd58",
            on_click=abrir_configuracion
        ),
        width= 250
    )

    boton_ordenes = ft.Container(
        content= ft.ElevatedButton(
            content=ft.Text(
                "Gestionar Órdenes",
                size=12,
                color="#000000",
                style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)
            ),
            bgcolor="#fddd58",
            on_click=abrir_ordenes
        ),
        width= 250
    )
    boton_resumen = ft.Container(
        content= ft.ElevatedButton(
            content=ft.Text(
                "Ver Resumen",
                size=12,
                color="#000000",
                style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)
            ),
            bgcolor="#fddd58",
            on_click=ver_resumen_cartones
        ),
        width= 250
    )

    layout = ft.Column([
            logo,
            ft.Text("Panel de Control", size=26, weight="bold"),
            boton_config,
            boton_ordenes,
            boton_resumen,
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    page.controls.clear()
    page.add(ft.Container(
            content=layout,
            alignment=ft.alignment.center,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#000000","#101010","#1e1e1e","#343434","#404040","#292929","#121212"]
            )
        ) 
    )
    page.update()

def mostrar_configuracion(page: ft.Page):
    rpc_name = "reiniciar_todos_los_cartones"  # Ajusta cuando crees la RPC

    # Obtener filas y convertir a dict {clave: valor}
    try:
        response = supa.table("configuracion").select("*").execute()
        rows = response.data if hasattr(response, "data") else (response.get("data") if isinstance(response, dict) else [])
    except Exception as ex:
        rows = []
        print("Error obteniendo configuración:", ex)

    config = {}
    for item in rows:
        clave = item.get("clave")
        valor = item.get("valor")
        if clave:
            config[clave] = valor

    controles = []
    entradas = {}

    # SnackBar (crear si no existe)
    if not hasattr(page, "snack_bar") or page.snack_bar is None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("", color="#ffffff"),
            bgcolor="#711616",
            duration=3000,
        )
    else:
        page.snack_bar.content = ft.Text("", color="#ffffff")
        page.snack_bar.bgcolor = "#711616"

    if page.snack_bar not in page.overlay:
        page.overlay.append(page.snack_bar)

    # --- 1) Switch de estado de venta (siempre arriba) ---
    estado_venta = config.get("venta_activa")
    estado_bool = estado_venta == 1 or estado_venta == "1" or estado_venta is True
    venta_activa_switch = ft.Row([ft.Switch(label="Estado de Venta", value=estado_bool)], expand=True, alignment=ft.MainAxisAlignment.CENTER)
    controles.append(venta_activa_switch)
    entradas["venta_activa"] = venta_activa_switch

    # --- 2) Botón Reiniciar (colocado justo después del switch) ---
    # definimos el botón y su contenedor con padding para dar espacio vertical
    boton_reiniciar_btn = ft.ElevatedButton(
        content=ft.Text("Reiniciar todos los cartones", size=12, color="#FFFFFF",
                        style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)),
        bgcolor="#ff5722",
        on_click=None  # lo asignaremos más abajo
    )
    boton_reiniciar_container = ft.Container(
        content=boton_reiniciar_btn,
        width=360,
        padding=ft.padding.only(top=10, bottom=10)  # espacio vertical para que no quede pegado
    )
    controles.append(boton_reiniciar_container)

    # --- 3) Divider ---
    controles.append(ft.Divider())

    # --- 4) Ahora el resto de campos en el orden deseado ---
    # Lista de claves en el orden preferido después del divider
    ordered_keys = [
        "tiempo_reserva_segundos",
        "precio_carton",
        "cartones_en_juego",
        "banco_pago",
        "telefono_pago",
        "ced_pago",
        "modo_de_juego",
        "reglamento"
    ]

    # Helper para crear TextField genérico
    def make_textfield(label, value, width=300, **kwargs):
        return ft.TextField(label=label, value=str(value) if value is not None else "", width=width, **kwargs)

    # Agregar campos por el orden preferido, si existen en config. Si no existen, los creamos vacíos más abajo.
    for key in ordered_keys:
        if key in ["modo_de_juego", "reglamento"]:
            # Manejo especial: contenedor con altura fija y TextField multiline
            val = config.get(key, "")
            if key == "modo_de_juego":
                modo_tf = ft.TextField(label="Modo de juego", value=str(val), multiline=True, expand=True)
                modo_container = ft.Container(content=modo_tf, width=720, height=160, padding=8)
                controles.append(modo_container)
                entradas["modo_de_juego"] = modo_tf
            else:  # reglamento
                regl_tf = ft.TextField(label="Reglamento", value=str(val), multiline=True, expand=True)
                regl_container = ft.Container(content=regl_tf, width=720, height=260, padding=8)
                controles.append(regl_container)
                entradas["reglamento"] = regl_tf
        else:
            if key in config:
                val = config.get(key, "")
                if key == "tiempo_reserva_segundos":
                    minutos = 0
                    try:
                        minutos = int(val) // 60
                    except Exception:
                        minutos = 0
                    tf = make_textfield("Tiempo de reserva (minutos)", minutos, width=300, keyboard_type=ft.KeyboardType.NUMBER)
                    entradas["tiempo_reserva_segundos"] = tf
                    controles.append(tf)

                elif key == "precio_carton":
                    precio_str = "0.00"
                    try:
                        precio_str = f"{float(val):.2f}"
                    except Exception:
                        precio_str = str(val)
                    tf = make_textfield("Precio del cartón", precio_str, width=300, keyboard_type=ft.KeyboardType.NUMBER)
                    entradas["precio_carton"] = tf
                    controles.append(tf)

                elif key == "cartones_en_juego":
                    tf = make_textfield("Cantidad de Cartones", val, width=300, keyboard_type=ft.KeyboardType.NUMBER)
                    entradas["cartones_en_juego"] = tf
                    controles.append(tf)

                elif key == "banco_pago":
                    tf = make_textfield("Banco (Pago Móvil)", val, width=300, keyboard_type=ft.KeyboardType.TEXT, max_length=10)
                    entradas["banco_pago"] = tf
                    controles.append(tf)

                elif key == "telefono_pago":
                    # formateador local
                    def make_telefono_field(initial):
                        def formatear_telefono(e):
                            texto = telefono_input.value
                            digitos = ''.join(filter(str.isdigit, texto))[:11]
                            formateado = ""
                            if len(digitos) >= 1:
                                formateado += digitos[:4]
                            if len(digitos) >= 5:
                                formateado += "-" + digitos[4:11]
                            telefono_input.value = formateado
                            page.update()

                        telefono_input = ft.TextField(
                            label="Teléfono (Pago Móvil)",
                            value=str(initial),
                            width=300,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            max_length=12,
                            on_change=formatear_telefono
                        )
                        return telefono_input

                    telefono_input = make_telefono_field(config.get("telefono_pago", ""))
                    entradas["telefono_pago"] = telefono_input
                    controles.append(telefono_input)

                elif key == "ced_pago":
                    def make_ced_field(initial):
                        def formatear_cedula(e):
                            texto = cedula_input.value
                            digitos = ''.join(filter(str.isdigit, texto))[:8]
                            formateado = ""
                            if len(digitos) >= 1:
                                formateado += digitos[:2]
                            if len(digitos) >= 3:
                                formateado += "." + digitos[2:5]
                            if len(digitos) >= 6:
                                formateado += "." + digitos[5:8]
                            cedula_input.value = formateado
                            page.update()

                        cedula_input = ft.TextField(
                            label="Cédula (Pago Móvil)",
                            value=str(initial),
                            width=300,
                            keyboard_type=ft.KeyboardType.NUMBER,
                            max_length=10,
                            on_change=formatear_cedula
                        )
                        return cedula_input

                    cedula_input = make_ced_field(config.get("ced_pago", ""))
                    entradas["ced_pago"] = cedula_input
                    controles.append(cedula_input)

    # Agregar cualquier otra clave que no esté en ordered_keys (campos genéricos)
    for k, v in config.items():
        if k in entradas:
            continue
        campo = make_textfield(k, v, width=300)
        controles.append(campo)
        entradas[k] = campo

    # Asegurarnos de que siempre existan los campos modo_de_juego y reglamento (vacíos si no existen)
    if "modo_de_juego" not in entradas:
        modo_tf = ft.TextField(label="Modo de juego", value="", multiline=True, expand=True)
        modo_container = ft.Container(content=modo_tf, width=720, height=160, padding=8)
        controles.append(modo_container)
        entradas["modo_de_juego"] = modo_tf

    if "reglamento" not in entradas:
        regl_tf = ft.TextField(label="Reglamento", value="", multiline=True, expand=True)
        regl_container = ft.Container(content=regl_tf, width=720, height=260, padding=8)
        controles.append(regl_container)
        entradas["reglamento"] = regl_tf

    # --- Función Guardar (igual lógica que antes) ---
    def guardar(e):
        errores = []
        updates = []

        for clave, widget in entradas.items():
            if clave == "venta_activa":
                valor = 1 if widget.value else 0

            elif clave == "tiempo_reserva_segundos":
                try:
                    minutos = int(widget.value)
                    valor = minutos * 60
                except Exception:
                    errores.append("Tiempo de reserva debe ser un número entero (minutos)")
                    continue

            elif clave == "precio_carton":
                try:
                    valor = round(float(widget.value), 2)
                except Exception:
                    errores.append("Precio del cartón debe ser un número válido con punto decimal")
                    continue

            elif clave == "cartones_en_juego":
                try:
                    valor = int(widget.value)
                except Exception:
                    errores.append("Ingrese un valor válido para los cartones en juego")
                    continue

            else:
                valor = widget.value

            updates.append((clave, valor))

        if errores:
            page.snack_bar.content = ft.Text("\n".join(errores), color="white")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return

        # Guardar (update o insert si no existe)
        for clave, valor in updates:
            try:
                supa.table("configuracion").update({"valor": valor}).eq("clave", clave).execute()
                # Verificar si existe, si no insertar
                existe = supa.table("configuracion").select("clave").eq("clave", clave).execute()
                if (hasattr(existe, "data") and (existe.data is None or len(existe.data) == 0)) or (isinstance(existe, dict) and not existe.get("data")):
                    supa.table("configuracion").insert({"clave": clave, "valor": valor}).execute()
            except Exception as ex:
                page.snack_bar.content = ft.Text(f"Error guardando {clave}: {ex}", color="white")
                page.snack_bar.bgcolor = "#d21e1e"
                page.snack_bar.open = True
                page.update()
                return

        page.snack_bar.content = ft.Text("Configuración actualizada", color="white")
        page.snack_bar.bgcolor = "#4caf50"
        page.snack_bar.open = True
        page.update()

    # --- RPC: ejecutar reinicio ---
    def reiniciar_cartones_rpc():
        boton_reiniciar_btn.disabled = True
        page.update()
        try:
            res = supa.rpc(rpc_name).execute()
            error = getattr(res, "error", None) or (res.get("error") if isinstance(res, dict) else None)
            data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)

            if error:
                msg = error if isinstance(error, str) else str(error)
                page.snack_bar.content = ft.Text(f"Error al reiniciar: {msg}", color="white")
                page.snack_bar.bgcolor = "#d21e1e"
            else:
                if data:
                    if isinstance(data, (list, tuple)) and len(data) > 0:
                        posible = data[0]
                        msg = posible.get("message") if isinstance(posible, dict) and "message" in posible else str(posible)
                    elif isinstance(data, dict) and "message" in data:
                        msg = data["message"]
                    else:
                        msg = "Reinicio completado correctamente."
                else:
                    msg = "Reinicio completado correctamente."
                page.snack_bar.content = ft.Text(str(msg), color="white")
                page.snack_bar.bgcolor = "#4caf50"

        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error en RPC: {ex}", color="white")
            page.snack_bar.bgcolor = "#d21e1e"
        finally:
            page.snack_bar.open = True
            boton_reiniciar_btn.disabled = False
            page.update()

    # --- Dialogo de confirmación ---
    confirmar_reinicio_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar reinicio", weight="bold"),
        content=ft.Text("¿Estás seguro que querés reiniciar TODOS los cartones? Esta acción no se puede deshacer."),
        actions=[]
    )

    def abrir_confirm(e):
        # añadir dialog al overlay si no está y abrir
        if confirmar_reinicio_dialog not in page.overlay:
            page.overlay.append(confirmar_reinicio_dialog)
        confirmar_reinicio_dialog.open = True
        page.update()

    def cerrar_confirm(e):
        confirmar_reinicio_dialog.open = False
        mostrar_configuracion(page=page)


    def confirmar_ejecutar(e):
        confirmar_reinicio_dialog.open = False
        mostrar_configuracion(page=page)
        reiniciar_cartones_rpc()

    # asignar acciones a los botones del dialog y al boton reiniciar
    confirmar_reinicio_dialog.actions = [
        ft.TextButton("Cancelar", on_click=cerrar_confirm),
        ft.ElevatedButton("Confirmar", on_click=confirmar_ejecutar, bgcolor="#ff2626")
    ]
    boton_reiniciar_btn.on_click = abrir_confirm

    # --- Botones inferiores: Guardar y Volver ---
    boton_guardar = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("Guardar Cambios", size=12, color="#000000",
                            style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)),
            bgcolor="#fddd58",
            on_click=guardar
        ),
        width=250
    )

    boton_volver = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("Volver", size=12, color="#FFFFFF",
                            style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)),
            bgcolor="#ff2626",
            on_click=lambda e: cargar_panel_admin(page)
        ),
        width=250
    )

    # Añadimos los botones inferiores al final de la columna
    controles.append(ft.Row([boton_guardar, boton_volver], alignment=ft.MainAxisAlignment.CENTER, spacing=20))

    # Layout principal: columna scrolleable
    main_column = ft.Column(
        [
            ft.Text("Configuración", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            *controles,
            ft.Container(height=20)
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.controls.clear()
    page.add(
        ft.Container(
            content=main_column,
            alignment=ft.alignment.center,
            expand=True,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#000000", "#101010", "#1e1e1e", "#343434", "#404040", "#292929", "#121212"]
            )
        )
    )

    page.update()

def mostrar_ordenes(page: ft.Page):
    # — Limpieza y snackbar —
    page.controls.clear()
    page.snack_bar = ft.SnackBar(content=ft.Text(""), duration=2000)
    page.overlay.append(page.snack_bar)

    # — Fijar tamaño de ventana (si lo necesitas) —
    page.window_width = 360
    page.window_height = 640

    # — Estado / datos —
    all_orders = []
    page_size = 100
    page_index = 0            # 0-based
    has_more = False
    status_filter = "pendiente"  # "pendiente" | "aprobada" | "rechazada"

    # — Modales: imagen y confirmación (reutilizables) —
    image_control = ft.Image(src="", width=300, height=300, fit=ft.ImageFit.CONTAIN)
    image_dialog = ft.AlertDialog(
        modal=True,
        content=image_control,
        actions=[ft.TextButton("Cerrar", on_click=lambda e: close_image())]
    )
    page.dialog = image_dialog
    page.overlay.append(image_dialog)

    def close_image():
        image_dialog.open = False
        page.update()

    confirm_dialog = ft.AlertDialog(modal=True, content=ft.Text(""), actions=[])
    page.overlay.append(confirm_dialog)

    def open_confirm(orden: str, aprovar: bool):
        accion_text = "aprobar" if aprovar else "rechazar"
        confirm_dialog.content = ft.Text(f"¿Deseas {accion_text} la orden {orden}?")
        def do_confirm(e):
            if aprovar:
                supa.rpc("aprobar_orden", {"p_numero_orden": orden}).execute()
            else:
                supa.rpc("liberar_cartones_por_orden_rechazada", {"p_numero_orden": orden}).execute()
            confirm_dialog.open = False
            page.snack_bar.content = ft.Text(f"Orden {orden} {'aprobada' if aprovar else 'rechazada'}")
            page.snack_bar.bgcolor = "#19b01b" if aprovar else "#d21e1e"
            page.snack_bar.open = True
            cargar_datos()
            page.update()

        def cancel_confirm(e):
            confirm_dialog.open = False
            page.update()

        confirm_dialog.actions = [
            ft.TextButton("Cancelar", on_click=cancel_confirm),
            ft.TextButton("Confirmar", on_click=do_confirm),
        ]
        confirm_dialog.open = True
        page.update()

    # — Preview imagen —
    def ver_imagen(e, url):
        if not url:
            page.snack_bar.content = ft.Text("No hay comprobante disponible")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return
        url_limpia = url.split("?")[0]
        if not url_limpia.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            page.snack_bar.content = ft.Text("La URL no apunta a una imagen válida")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return
        image_control.src = url_limpia
        image_control.update()
        image_dialog.open = True
        page.update()

    # — Encabezado (mejor organizado) —
    title = ft.Text(
        "Gestión de Órdenes",
        size=26, weight="bold", color="#fddd58",
        style=ft.TextStyle(font_family="BingoFont")
    )
    logo = ft.Image(src="solo_logo.png", width=72, height=54, fit=ft.ImageFit.CONTAIN)

    # botones pequeños en el header (export / volver) -- se mantienen funcionales
    btn_export_header = ft.IconButton(ft.Icons.FILE_DOWNLOAD, tooltip="Exportar", on_click=lambda e: exportar_excel(e))
    btn_volver_header = ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: cargar_panel_admin(page))

    header = ft.Row(
        controls=[
            logo,
            ft.Container(content=title, expand=True, alignment=ft.alignment.center_left),
            ft.Row([btn_export_header, btn_volver_header], spacing=6)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # — DataTable — (columnas idénticas, sin tocar la lógica)
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Orden")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Cant.")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Ref.")),
            ft.DataColumn(ft.Text("Comp.")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
        heading_row_color="#333333",
        heading_text_style=ft.TextStyle(color="#fddd58", weight=ft.FontWeight.BOLD),
        data_row_color="#222222",
        expand=True,
    )

    def cargar_tabla():
        tabla.rows.clear()
        for o in all_orders:
            fecha = datetime.fromisoformat(o["fecha_creacion"]).strftime("%d/%m %H:%M")
            comprobante_url = o.get("comprobante", "").split("?")[0]
            btn_ver = ft.IconButton(ft.Icons.PHOTO, on_click=lambda e, url=comprobante_url: ver_imagen(e, url))

            estatus_val = o.get("estatus")
            is_pending = (estatus_val is None) or (str(estatus_val).strip() == "")

            if is_pending:
                btn_aprobar = ft.ElevatedButton("✔", width=40, on_click=lambda e, n=o["numero_orden"]: open_confirm(n, True))
                btn_rechazar = ft.ElevatedButton("✖", width=40, on_click=lambda e, n=o["numero_orden"]: open_confirm(n, False))
                acciones_cell = ft.Row([btn_aprobar, btn_rechazar], spacing=6)
            else:
                acciones_cell = ft.Text("-")

            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(o["numero_orden"])),
                    ft.DataCell(ft.Text(o["nombre"])),
                    ft.DataCell(ft.Text(o["telefono"])),
                    ft.DataCell(ft.Text(f"{o['monto']:.2f}")),
                    ft.DataCell(ft.Text(str(o["cantidad_cartones"]))),
                    ft.DataCell(ft.Text(fecha)),
                    ft.DataCell(ft.Text(o.get("referencia", "-"))),
                    ft.DataCell(btn_ver),
                    ft.DataCell(acciones_cell),
                ])
            )
        page.update()

    # — Exportar a Excel (igual que antes) —
    def exportar_excel(e):
        if not all_orders:
            page.snack_bar.content = ft.Text("No hay datos para exportar")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Órdenes"
        headers = ["Orden", "Nombre", "Teléfono", "Monto", "Cantidad", "Fecha", "Referencia", "Comprobante"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for o in all_orders:
            fecha = datetime.fromisoformat(o["fecha_creacion"]).strftime("%d/%m %H:%M")
            ws.append([
                o["numero_orden"], o["nombre"], o["telefono"],
                o["monto"], o["cantidad_cartones"], fecha,
                o.get("referencia", ""), o.get("comprobante", "")
            ])

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            wb.save(tmp_file.name)
            tmp_file.seek(0)
            b64 = base64.b64encode(tmp_file.read()).decode()

        download_link = ft.TextButton(
            "Descargar Excel",
            url=f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}",
            style=ft.ButtonStyle(color="#ffffff", bgcolor="#3a8ee6"),
        )

        page.snack_bar.content = ft.Row([
            ft.Text("Exportación lista"),
            download_link
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        page.snack_bar.bgcolor = "#1e90ff"
        page.snack_bar.open = True
        page.update()

    # — Cargar datos desde Supabase (con filtro y paginación) —
    def cargar_datos():
        nonlocal all_orders, has_more, page_index
        start = page_index * page_size
        end = start + page_size - 1

        query = supa.table("ordenes").select("*").order("fecha_creacion", desc=True).range(start, end)

        if status_filter == "pendiente":
            query = query.is_("estatus", None)
        elif status_filter == "aprobada":
            query = query.eq("estatus", "APROBADA")
        elif status_filter == "rechazada":
            query = query.eq("estatus", "RECHAZADA")

        res = query.execute()
        data = res.data or []
        all_orders = data
        has_more = len(data) == page_size

        cargar_tabla()

        btn_prev.disabled = (page_index == 0)
        btn_next.disabled = (not has_more)
        lbl_page.value = f"Página {page_index + 1}"
        page.update()

    # — Filtros (arriba, con look mejorado) —
    def set_filter(f):
        nonlocal status_filter, page_index
        status_filter = f
        page_index = 0
        actualizar_filtros_ui()
        cargar_datos()

    def actualizar_filtros_ui():
        if status_filter == "pendiente":
            btn_pendiente.bgcolor, btn_pendiente.color = "#fddd58", "#000000"
            btn_aprobada.bgcolor, btn_aprobada.color = "#444444", "#ffffff"
            btn_rechazada.bgcolor, btn_rechazada.color = "#444444", "#ffffff"
        elif status_filter == "aprobada":
            btn_pendiente.bgcolor, btn_pendiente.color = "#444444", "#ffffff"
            btn_aprobada.bgcolor, btn_aprobada.color = "#19b01b", "#ffffff"
            btn_rechazada.bgcolor, btn_rechazada.color = "#444444", "#ffffff"
        else:
            btn_pendiente.bgcolor, btn_pendiente.color = "#444444", "#ffffff"
            btn_aprobada.bgcolor, btn_aprobada.color = "#444444", "#ffffff"
            btn_rechazada.bgcolor, btn_rechazada.color = "#d21e1e", "#ffffff"
        page.update()

    btn_pendiente = ft.ElevatedButton("Pendientes", on_click=lambda e: set_filter("pendiente"))
    btn_aprobada = ft.ElevatedButton("Aprobadas", on_click=lambda e: set_filter("aprobada"))
    btn_rechazada = ft.ElevatedButton("Rechazadas", on_click=lambda e: set_filter("rechazada"))
    filtros_row = ft.Row([btn_pendiente, btn_aprobada, btn_rechazada], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
    actualizar_filtros_ui()

    # — Paginación (debajo de la tabla) —
    def ir_anterior(e):
        nonlocal page_index
        if page_index > 0:
            page_index -= 1
            cargar_datos()

    def ir_siguiente(e):
        nonlocal page_index
        if has_more:
            page_index += 1
            cargar_datos()

    btn_prev = ft.ElevatedButton("« Anterior", on_click=ir_anterior, disabled=True)
    btn_next = ft.ElevatedButton("Siguiente »", on_click=ir_siguiente, disabled=True)
    lbl_page = ft.Text(f"Página {page_index + 1}")
    paginacion_row = ft.Row([btn_prev, lbl_page, btn_next], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    # — Botones inferiores (compactos) —
    btn_exportar = ft.ElevatedButton("Exportar a Excel", bgcolor="#3a8ee6", on_click=exportar_excel)
    btn_volver = ft.ElevatedButton("Volver", bgcolor="#ff2626", on_click=lambda e: cargar_panel_admin(page))

    # — Contenedor central (card-like) que contiene la tabla — 
    # ancho máximo para que se vea centrado en pantallas más anchas
    max_inner_width = min(page.window_width - 40, 900)

    table_card = ft.Container(
        expand=True,
        padding=12,
        border_radius=12,
        border=ft.border.all(1, "#2b2b2b"),
        bgcolor="#0f0f0f",
        content=ft.Column([
            filtros_row,
            ft.Divider(thickness=1, color="#2b2b2b"),
            # área de tabla con alto fijo => scroll interno
            ft.Container(
                content=ft.Row([tabla], scroll=ft.ScrollMode.AUTO),
                height=360,  # ajustable según preferencia

            ),
            ft.Row([paginacion_row], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ], spacing=8)
    )

    # — Montaje final: header + card centrado + botones inferiores —
    layout = ft.Column([
        header,
        ft.Container(content=table_card, alignment=ft.alignment.center, expand=True)
       # ft.Row([btn_exportar, btn_volver], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    ], expand=True, spacing=12)

    background = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#000000", "#1e1e1e", "#292929"]
        ),
        content=ft.Container(content=layout, padding=16)
    )

    page.add(background)
    page.update()
    cargar_datos()

def mostrar_resumen_cartones(page: ft.Page):
    # limpiar y preparar
    page.controls.clear()
    page.snack_bar = ft.SnackBar(content=ft.Text(""), duration=2000)
    page.overlay.append(page.snack_bar)

    # Column que contendrá las líneas
    list_column = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO, width=210)
    # Container scrolleable vertical que envuelve la columna
    list_container = ft.Container(
        content=list_column,
        height=420,                # alto del área scrollable
        width=None,
        padding=ft.padding.all(8),
        bgcolor="#0b0b0b",
        border=ft.border.all(1, "#222222"),
        border_radius=8,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Listado de Cartones", weight="bold", size=18),
        content=ft.Column([
            ft.Text("✅: Verificados, ⚠️: Por Verificar", size=12),
            ft.Divider(),
            list_container,
        ], spacing=8),
        actions=[]
    )
    page.overlay.append(dialog)

    # Mapa dígito -> emoji
    DIGIT_EMOJI = {
        "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣",
        "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣",
    }

    def number_to_emoji(n: int, width: int = 3) -> str:
        s = str(int(n)).zfill(width)
        return "".join(DIGIT_EMOJI.get(ch, ch) for ch in s)

    def _format_line(n, info, num_width):
        """
        info: dict con keys: 'jugador', 'estatus_pago', 'numero_orden' (según tu consulta)
        estatus_pago: 0 => disponible, 1 => pendiente (⚠️), 2 => verificado (✅)
        """
        jugador = info.get("jugador") if info else None
        estatus_pago = info.get("estatus_pago") if info else None
        numero_orden = info.get("numero_orden") if info else None

        # normalizar estatus_pago a int si puede ser str
        try:
            ep = int(estatus_pago) if estatus_pago is not None else None
        except Exception:
            ep = None

        mark = ""
        if ep == 2:
            mark = "✅"
        elif ep == 1:
            mark = "⚠️"
        # ep == 0 o None => disponible (sin marca)

        emoji_num = number_to_emoji(n, num_width)

        if jugador:
            # quitar espacios innecesarios
            parts = [emoji_num, str(jugador)]
            if mark:
                parts.append(mark)
            return " ".join(parts)
        else:
            # sin jugador
            if mark:
                return f"{emoji_num} {mark}"
            else:
                return f"{emoji_num}"

    def cargar_lista(e=None):
        # obtener número de cartones activos
        try:
            res = supa.table("configuracion").select("valor").eq("clave", "cartones_en_juego").execute()
            ncartones = int(res.data[0]["valor"])
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error leyendo configuración: {ex}")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return

        # leer todos los cartones (ajusta campos si en tu BD se llaman distinto)
        try:
            # uso ncarton, jugador, estatus_pago, numero_orden según tu modificación previa
            resp = supa.table("cartones").select("ncarton, jugador, estatus_pago, numero_orden").execute()
            cartones_data = resp.data or []
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"Error leyendo cartones: {ex}")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return

        # indexar por número
        by_num = {}
        for c in cartones_data:
            num = c.get("ncarton")
            if num is None:
                continue
            try:
                key = int(num)
            except Exception:
                # ignorar si no convertible
                continue
            by_num[key] = c

        # decidir ancho (digits) para emojis según ncartones
        num_width = max(3, len(str(ncartones)))

        # reconstruir UI
        list_column.controls.clear()
        lines_for_copy = []
        for i in range(1, ncartones + 1):
            info = by_num.get(i, {})
            line_text = _format_line(i, info, num_width)
            lines_for_copy.append(line_text)
            # mostrar línea; la prop selectable=True permite al usuario seleccionar/copiar también
            txt = ft.Text(line_text, selectable=True)
            list_column.controls.append(txt)

        # guardar copiable
        dialog.data = {"copiable_text": "\n".join(lines_for_copy)}

        # refrescar
        list_column.update()
        list_container.update()
        dialog.update()
        page.update()

    # acciones del dialog
    def accion_refrescar(e):
        cargar_lista()
        page.snack_bar.content = ft.Text("Lista actualizada")
        page.snack_bar.bgcolor = "#19b01b"
        page.snack_bar.open = True
        page.update()

    def accion_copiar(e):
        txt = (dialog.data or {}).get("copiable_text", "")
        if not txt:
            page.snack_bar.content = ft.Text("Nada para copiar")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()
            return
        try:
            # intentamos copiar al clipboard del page (si tu versión de flet soporta)
            page.set_clipboard(txt)
            page.snack_bar.content = ft.Text("Listado copiado al portapapeles")
            page.snack_bar.bgcolor = "#19b01b"
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar.content = ft.Text(f"No pude copiar: {ex}")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            page.update()

    def accion_cerrar(e):
        dialog.open = False
        cargar_panel_admin(page)

    dialog.actions = [
        ft.ElevatedButton("Refrescar", on_click=accion_refrescar),
        ft.ElevatedButton("Copiar", on_click=accion_copiar),
        ft.ElevatedButton("Cerrar", on_click=accion_cerrar, bgcolor="#ff2626"),
    ]

    # abrir modal y cargar datos
    dialog.open = True
    page.update()
    cargar_lista()

if __name__ == "__main__":
    ft.app(target=admin_login, view=ft.WEB_BROWSER, assets_dir=".", port=8550)
