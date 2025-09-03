import flet as ft
from supabase_client import supa  # Asegúrate de que esté correctamente configurado
from flet import TextOverflow
from datetime import datetime
import uuid
import os
import asyncio

def obtener_datos_pago():
    try:
        response = supa.rpc("get_datos_pago").execute()

        if response.data and isinstance(response.data, list) and len(response.data) > 0:
            datos = response.data[0]
            banco = datos.get("banco")
            telefono = datos.get("telefono")
            cedula = datos.get("cedula")

            return banco, telefono, cedula
        else:
            print("No se encontraron datos de pago.")
            return None, None, None

    except Exception as e:
        print("Error consultando datos de pago:", e)
        return None, None, None

def subir_pago(page: ft.Page):
    # Recuperar datos de sesión
    page.controls.clear()
    data = page.session_data
    numero_orden = data.get("numero_orden", "")
    monto        = data.get("monto", 0.0)

    page.snack_bar = ft.SnackBar(
    content=ft.Text("",color="#ffffff"),
    bgcolor="#711616",
    duration=2000,
    )

    banco, telefono, cedula = obtener_datos_pago()

    page.overlay.append(page.snack_bar)
    # Campo de referencia
    ref_input = ft.TextField(
        hint_text="Referencia (Últimos 6 Dígitos)",
        width=300,
        height=50,
        border_radius=6,
        text_align="start",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color="#090909", size=12),
        bgcolor="#FFFFFF",
        focused_border_color="#fddd58"
    )

    logo = ft.Image(
            src="solo_logo.png",
            width=100,
            height=74,
            fit=ft.ImageFit.CONTAIN
        )
    
    texto = ft.Image(
            src="ya_casi.png",
            width=280,
            height=50,
            fit=ft.ImageFit.CONTAIN
        )

    header = ft.Column(
        controls=[logo, texto],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )
        # Línea divisoria
    linea_divisoria = ft.Container(
        height=1,
        width=350,
        bgcolor="#fddd58",
        margin=ft.Margin(0, 1, 0, 1),
    )

    linea_divisoria_vertical = ft.Container(
        height=50,
        width=1,
        bgcolor="#fddd58",
        margin=ft.Margin(1, 0, 1, 0),
    )



    # Copiar datos
    def copiar_datos(e):
        texto = (
            f"Banco: {banco}\n"
            f"Cédula: {cedula}\n"
            f"Teléfono: {telefono}\n"
            f"Monto: {monto:.2f} BsD"
        )

        page.set_clipboard(texto)
        
        page.snack_bar.content.value = "Datos copiados al portapapeles"
        page.snack_bar.bgcolor = "#19b01b"
        page.snack_bar.open = True
        page.update()

    boton_copiar = ft.ElevatedButton(
        content=ft.Text(
            "Copiar Datos",
            size=10,
            color="#000000",
            style=ft.TextStyle(font_family="Arial")
        ),
        width=100,
        height=30,
        style=ft.ButtonStyle(
            bgcolor="#fddd58",
            color="#000000",
            side=ft.BorderSide(2, "#000000"),
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=lambda e: copiar_datos(e)
    )

    pago_movil = ft.Container(
        bgcolor="#fddd58",
        padding=0,
        border_radius=10,
        border=ft.border.all(2, "#fddd58"),
        content=ft.Column(
            controls=[
                ft.Container(
                bgcolor="#000000",
                padding=10,
                border_radius=10,
                content=
                ft.Row(
                    controls=[
                        ft.Column([
                            ft.Text("Banco", size=20, color="#fddd58",
                                    style=ft.TextStyle(font_family="BingoFont")),
                            ft.Text(banco, size=14, weight="bold", color="white",
                                    style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD))
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        tight=True                        
                        ),
                        linea_divisoria_vertical,
                        ft.Column([
                            ft.Text("Cédula", size=20, color="#fddd58",
                                    style=ft.TextStyle(font_family="BingoFont")),
                            ft.Text(cedula, size=14, weight="bold", color="white",
                                    style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD))
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        tight=True                        
                        ),
                        linea_divisoria_vertical,
                        ft.Column([
                            ft.Text("Teléfono", size=20, color="#fddd58",
                                    style=ft.TextStyle(font_family="BingoFont")),
                            ft.Text(telefono, size=14, weight="bold", color="white",
                                    style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD))
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )),
                # Fila con Total y botón copiar
                ft.Container(
                    bgcolor="#fddd58",
                    padding=ft.padding.symmetric(vertical=2, horizontal=5),
                    border_radius=6,
                    content=ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(f"Total a Pagar:",
                                            size=23, color="#000000",
                                            style=ft.TextStyle(font_family="BingoFont")),
                                    ft.Text(f"{monto:.2f} BsD",
                                            size=16, color="#000000",
                                            style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD))],
                                spacing=5,
                            ),
                            boton_copiar
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5
                    )
                )
            ],
            spacing=0,
            tight=True
        )
    )

    def cancelar_y_volver_a_seleccion(page, numero_orden):
        def confirmar_cancelacion(e):
            dlg.open = False
            page.update()

            # Ejecutar el RPC de cancelación
            supa.rpc("cancelar_orden_rpc", {
                "p_numero_orden": numero_orden
            }).execute()

            from main import verificar_venta_activa
            if not verificar_venta_activa(page):
                return

            # Navegar a la pantalla de selección
            from view_seleccion import seleccion_cartones
            page.controls.clear()
            seleccion_cartones(page)
            page.update()

        def cerrar_dialogo(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Cancelar orden?"),
            content=ft.Text("Si regresas, tu orden será cancelada y los cartones seleccionados volverán a estar disponibles."),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.TextButton("Sí, cancelar y volver", on_click=confirmar_cancelacion),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def volver_a_main(page):
        from main import main  # import local para evitar circularidad
        page.controls.clear()
        main(page)
        page.update()

    def volver_a_seleccion(page):
        from view_seleccion import seleccion_cartones
        page.controls.clear()
        seleccion_cartones(page)
        page.update()
    
    # FilePicker y label
    archivo_label = ft.Text("Añadir Capture", color="#ffffff", size=20, style=ft.TextStyle(font_family="BingoFont"))
    # FilePicker
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    archivo_seleccionado = None
    upload_key = None

    def on_file_pick(e: ft.FilePickerResultEvent):
        nonlocal archivo_seleccionado
        print("📁 File picked:", e.files)

        if e.files:
            archivo_seleccionado = e.files[0]
            archivo_label.value = "Capture Añadido"
            archivo_label.color = "#168821"
            page.snack_bar.content = ft.Text("Archivo cargado correctamente")
            page.snack_bar.bgcolor = "#168821"
        else:
            archivo_seleccionado = None
            page.snack_bar.content = ft.Text("No se seleccionó archivo")
            page.snack_bar.bgcolor = "#d21e1e"

        page.snack_bar.open = True
        page.update()

    def on_file_upload(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0 and not e.error:
            # 1) Obtener URL pública
            url = supa.storage.from_("comprobantes").get_public_url(upload_key)

            # 2) Ejecutar el RPC para guardar info
            supa.rpc("actualizar_pago_rpc", {
                "p_numero_orden": numero_orden,
                "p_referencia":   ref_input.value,
                "p_storage_key":  url
            }).execute()

            # 3) Feedback
            page.snack_bar.content = ft.Text(
                "Pago registrado con éxito. Será verificado en breve.",
                color="#ffffff"
            )
            page.snack_bar.bgcolor = "#168821"
            page.snack_bar.open = True
            page.update()
            volver_a_main(page)

    file_picker.on_result = on_file_pick
    file_picker.on_upload = on_file_upload

    async def registrar_pago(e):
        nonlocal archivo_seleccionado, upload_key

        if not ref_input.value or archivo_seleccionado is None:
            page.snack_bar.content = ft.Text("Completa todos los campos")
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            await page.update()
            return

        # ✅ 1) Validar referencia y vigencia de la orden ANTES de subir
        resp = supa.rpc("validar_pago", {
            "p_numero_orden": numero_orden,
            "p_referencia":   ref_input.value
        }).single().execute()

        result = resp.data or {}
        ref_unica    = result.get("ref_unica", False)
        orden_activa = result.get("orden_activa", False)

        if not ref_unica:
            page.snack_bar.content = ft.Text(
                f"La referencia ‘{ref_input.value}’ ya está en uso.",
                color="#ffffff"
            )
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            await page.update()
            return

        if not orden_activa:
            page.snack_bar.content = ft.Text(
                "La orden ha expirado. Selecciona cartones de nuevo.",
                color="#ffffff"
            )
            page.snack_bar.bgcolor = "#d21e1e"
            page.snack_bar.open = True
            await page.update()
            volver_a_seleccion(page)
            return

        # ✅ 2) Si todo fue validado, generar upload_key
        extension = os.path.splitext(archivo_seleccionado.name)[-1].lower()
        upload_key = f"comprobantes/{numero_orden}{extension}"

        # ✅ 3) Solicitar URL firmada
        signed_upload_resp = supa.storage \
            .from_("comprobantes") \
            .create_signed_upload_url(upload_key)

        signed_url = signed_upload_resp.get("signed_url") or signed_upload_resp.get("signedUrl")
        if not signed_url:
            raise RuntimeError(f"No pude extraer signed_url de {signed_upload_resp!r}")

        # ✅ 4) Lanzar la subida desde el navegador
        upload_list = [
            ft.FilePickerUploadFile(
                name=archivo_seleccionado.name,
                upload_url=signed_url,
                method="PUT",
            )
        ]
        file_picker.upload(upload_list)
        
    archivo_btn = ft.ElevatedButton(
    text="Seleccionar Archivo",
    width=200, height=35,
    bgcolor="#fddd58", color="#000000",
    on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )

    recuadro_reporte = ft.Container(
        bgcolor="#80000000",
        padding=20,
        border_radius=10,
        border=ft.border.all(2, "#fddd58"),
        content=ft.Column(
            controls=[
                ft.Text("Reporta tu pago", size=30, weight="bold", color="#fddd58", style=ft.TextStyle(font_family="BingoFont")),
                ref_input,
                ft.Row(
                    controls=[
                        archivo_label,
                        archivo_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    linea_divisoria,
                    ft.ElevatedButton(
                        "Enviar Comprobante",
                        width=page.window_width- 20, height=40,
                        bgcolor="#d21e1e", color="#ffffff",
                        on_click=registrar_pago
                    )],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    ))

    boton_volver = ft.ElevatedButton(
        content=ft.Text(
            "Volver a Selección",
            size=10,
            color="#ffffff",
            style=ft.TextStyle(font_family="Arial")
        ),
        bgcolor="#711616",
        on_click=lambda e: (
        print("Botón presionado"),
        cancelar_y_volver_a_seleccion(page, numero_orden=numero_orden)
    )
    )

    # Construir la View
    view = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            controls=[
                header,
                ft.Container(
                    width=page.window_width,
                    content=pago_movil),
                ft.Container(
                    width=page.window_width,    
                    content=recuadro_reporte),
                    ft.Container(
                    width=page.window_width,    
                    content=  boton_volver)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14
        )
    )

    background = ft.Container(
    expand=True,
    gradient=ft.LinearGradient(
        begin=ft.alignment.top_center,
        end=ft.alignment.bottom_center,
        colors=["#000000","#101010","#1e1e1e","#343434","#404040","#292929","#121212"]
    ),
    content=view
    )

    page.add(background)
    page.update()