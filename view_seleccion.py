import flet as ft
from supabase_client import supa
import asyncio
from flet import TextOverflow
import threading
from datetime import datetime
from cargar_pago import subir_pago
import time

polling_running = True  # <- VARIABLE GLOBAL

def seleccion_cartones(page: ft.Page):
    # Limpiamos la vista previa
    page.controls.clear()

    page.snack_bar = ft.SnackBar(
    content=ft.Text("",color="#ffffff"),
    bgcolor="#711616",
    duration=2000,
    )
    page.overlay.append(page.snack_bar)

    res = supa.table("configuracion").select("valor").eq("clave", "cartones_en_juego").execute()
    valor_str = res.data[0]["valor"]
    ncartones = int(valor_str)

    # Recuperamos datos de jugador
    nombre = page.session_data["nombre"]
    telefono = page.session_data["telefono"]

    consulta = supa.table("configuracion").select("valor").eq("clave", "precio_carton").execute()
    precio = consulta.data[0]["valor"]

    precio_unitario = float(precio)
    seleccion = page.session_data.setdefault("seleccion", set())

    # 1) Bienvenida: imagen + nombre, alineados a la izquierda internamente
    bienvenido = ft.Container(
        content=ft.Image(
            src="bienvenido.png",
            width=170,
            height=50
        ),
        alignment=ft.alignment.center_left,
        margin=ft.Margin(0, 0, 0, 0),
        padding=0
    )
    name = ft.Text(
        f" {nombre}",
        size=30,
        color="#ffffff",
        style=ft.TextStyle(font_family="BingoFont"),
        max_lines=1,                          # Solo una línea
        overflow=TextOverflow.ELLIPSIS        # Recorta con “…”
    )
    welcome = ft.Column(
        controls=[bienvenido, name],
        spacing=1,
        # ***** alineamos internamente a la izquierda *****
        horizontal_alignment=ft.CrossAxisAlignment.START
    )

    # 2) Logo a la derecha
    logo = ft.Image(
        src="solo_logo.png",
        width=100,
        height=74,
        fit=ft.ImageFit.CONTAIN
    )

    # 3) Línea divisoria
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

    # 4) Fila principal: welcome expande a la izquierda, logo a la derecha
    encabezado = ft.Row(
        controls=[
            # Le decimos a welcome que tome todo el espacio sobrante
            ft.Container(expand=True, content=welcome),
            logo
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        width=350  # o el ancho que prefieras
    )

    # 5) Combinamos con la línea en una columna
    encabezado_fila = ft.Column(
        controls=[encabezado, linea_divisoria],
        spacing=2,
        # Centrar la columna en su contenedor padre
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Controles de texto que se actualizarán dinámicamente
    lbl_cant = ft.Text(
        f"{len(seleccion)}",
        size=12,
        color="#ffffff",
        style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD)
    )

    lbl_tel = ft.Text(
        f"{telefono}",
        size=12,
        color="#ffffff",
        style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD),
        max_lines=1,
        overflow=TextOverflow.ELLIPSIS
    )

    lbl_precio = ft.Text(
        f"{(len(seleccion)*precio_unitario):.2f} BsD",
        size=12,
        color="#ffffff",
        style=ft.TextStyle(font_family="Arial", weight=ft.FontWeight.BOLD),
        max_lines=1,
        overflow=TextOverflow.ELLIPSIS
    )

    numero = ft.Column(
        controls=[
            ft.Text(
                "Tu número es",
                size=20,
                color="#fddd58",
                style=ft.TextStyle(font_family="BingoFont")
            ),
            lbl_tel
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=1,
        tight=True
    )

    cartones = ft.Column(
        controls=[
            ft.Text(
                "Cartones",
                size=20,
                color="#fddd58",
                style=ft.TextStyle(font_family="BingoFont")
            ),
            lbl_cant
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=1,
        tight=True
    )

    total = ft.Column(
        controls=[
            ft.Text(
                "Total a Pagar",
                size=20,
                color="#fddd58",
                style=ft.TextStyle(font_family="BingoFont")
            ),
            lbl_precio
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=1,
        tight=True
    )

    indicadores = ft.Row(
        controls=[
            numero,
            linea_divisoria_vertical,
            cartones,
            linea_divisoria_vertical,
            total
        ],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        wrap=False,
        width=page.window_width * 0.9
    )

    # ------------------
    # Header + Toggle + Grids
    # ------------------

    estatus = {}
    seleccion = page.session_data.setdefault("seleccion", set())
    current_tab = page.session_data.setdefault("tab", "numeros")

    # Helper para los botones de NÚMEROS (igual que antes)…
    def make_btn(n):
        state = estatus.get(n, 0)
        sel = n in seleccion
        if state == 1:
            bgcolor, color, disabled = "#711616", "#ffffff", True
        elif sel:
            bgcolor, color, disabled = "#fddd58", "#000000", False
        else:
            bgcolor, color, disabled = "#ffffff", "#000000", False
        return ft.ElevatedButton(
            text=n,
            width=60, height=60,
            bgcolor=bgcolor,
            color=color,
            disabled=disabled,
            on_click=lambda e, num=n: toggle_carton(num),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(8),
                text_style=ft.TextStyle(font_family="Arial", size=12, weight=ft.FontWeight.BOLD)
            )
        )

    # GridView de NÚMEROS
    grid_view = ft.GridView(
        expand=True, spacing=8, run_spacing=8,
        max_extent=80, child_aspect_ratio=2,
        controls=[make_btn(f"{i:03d}") for i in range(1, (ncartones+1))]
    )
    numeros_container = ft.Container(content=grid_view, height=350, width=None)

    # Nuevo helper: cada “card” de CARTÓN
    def make_carton_card(n):
        state = estatus.get(n, 0)
        sel = n in seleccion
        # Elegimos color de borde y texto de estatus
        if state == 1:
            border_color, txt, txt_color = "#711616", "Ocupado", "#ffffff"
            clickable = False
        elif sel:
            border_color, txt, txt_color = "#fddd58", "Seleccionado", "#000000"
            clickable = True
        else:
            border_color, txt, txt_color = "#ffffff", "Disponible", "#000000"
            clickable = True
        card = ft.Container(
            width=200, height=290,
            border=ft.border.all(3, border_color),
            border_radius=8,
            bgcolor=border_color,
            content=ft.Column(
                controls=[
                    ft.Image(
                        src=f"cartones/bingo_card_{int(n)}.png",
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=8
                    ),
                    ft.Container(
                        content=ft.Text(txt, size=12, color=txt_color),
                        alignment=ft.alignment.center,
                        padding=ft.Padding(6, 4, 6, 4),
                        bgcolor=border_color,
                    )
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        if clickable:
            card.on_click = lambda e, num=n: toggle_carton(num)
        return card

    # GridView de CARTONES
    cartones_grid = ft.GridView(
        expand=True, spacing=8, run_spacing=8,
        max_extent=200, child_aspect_ratio=200/290,
        controls=[make_carton_card(f"{i}") for i in range(1, (ncartones+1))]
    )
    cartones_container = ft.Container(content=cartones_grid, height=350, width=None)

    # Toggle buttons
    btn_numeros = ft.ElevatedButton("Números", expand=True, on_click=lambda e: switch_tab("numeros"))
    btn_cartones = ft.ElevatedButton("Cartones", expand=True, on_click=lambda e: switch_tab("cartones"))
    toggle = ft.Row([btn_numeros, btn_cartones], spacing=12, width=page.window_width * 0.9)

    # Funciones para el switch de pestañas
    def update_toggle_ui():
        nonlocal current_tab
        if current_tab == "numeros":
            btn_numeros.bgcolor, btn_numeros.color = "#fddd58", "#000000"
            btn_cartones.bgcolor, btn_cartones.color = "#ff2626", "#ffffff"
            numeros_container.visible = True
            cartones_container.visible = False
        else:
            btn_numeros.bgcolor, btn_numeros.color = "#ff2626", "#ffffff"
            btn_cartones.bgcolor, btn_cartones.color = "#fddd58", "#000000"
            numeros_container.visible = False
            cartones_container.visible = True
        page.update()

    def switch_tab(tab_name: str):
        nonlocal current_tab
        current_tab = tab_name
        page.session_data["tab"] = tab_name
        update_toggle_ui()


    # Container único que engloba todo
    header_con_grid = ft.Container(
        expand=True,
        bgcolor="#80000000",
        border=ft.border.all(2, "#fddd58"),
        border_radius=12,
        padding=12,
        content=ft.Column(
            controls=[
                ft.Text("Selecciona tus Cartones",
                        size=25, color="#fddd58",
                        style=ft.TextStyle(font_family="BingoFont")),
                toggle,
                numeros_container,
                cartones_container
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        )
    )

    async def polling_loop():
        global polling_running
        while polling_running:
            await fetch_status()
            await asyncio.sleep(3)

    def start_polling():
        global polling_running
        polling_running = True  # <- ACTIVAMOS EL LOOP
        threading.Thread(target=lambda: asyncio.run(polling_loop()), daemon=True).start()

    def detener_polling():
        global polling_running
        polling_running = False

    # Lógica para refrescar estados y selección
    async def fetch_status():
        resp = supa.rpc("get_cartones_status", {}).execute()
        nuevos_estatus = {}
        cartones_ocupados_durante_seleccion = []

        for r in resp.data:
            numero = f"{r['numero']:03d}"
            nuevos_estatus[numero] = r["status"]

            # Detectar si fue ocupado estando seleccionado
            if numero in seleccion and r["status"] == 1:
                seleccion.remove(numero)
                cartones_ocupados_durante_seleccion.append(numero)

        if cartones_ocupados_durante_seleccion:
            ocupados = list(cartones_ocupados_durante_seleccion)
            if len(ocupados) == 1:
                mensaje = f"El cartón {ocupados[0]} fue ocupado"
            else:
                lista = ", ".join(ocupados)
                mensaje = f"Los cartones {lista} fueron ocupados"

            page.snack_bar.content.value = mensaje
            page.snack_bar.open = True
            page.update()

        estatus.clear()
        estatus.update(nuevos_estatus)

        lbl_cant.value = str(len(seleccion))
        lbl_precio.value = f"{len(seleccion) * precio_unitario:.2f} BsD"

        _rebuild_all()
        page.update()


    def _rebuild_all():
        grid_view.controls     = [make_btn(f"{i:03d}")        for i in range(1, (ncartones+1))]
        cartones_grid.controls = [make_carton_card(f"{i:03d}") for i in range(1, (ncartones+1))]

    def toggle_carton(num):
        if num in seleccion:
            seleccion.remove(num)
        else:
            seleccion.add(num)
        lbl_cant.value   = str(len(seleccion))
        lbl_precio.value = f"{len(seleccion) * precio_unitario:.2f} BsD"
        _rebuild_all()
        page.update()

    def guardar_seleccion(e):
        
        from main import verificar_venta_activa
        if not verificar_venta_activa(page):
            return
        
        if not seleccion:
            page.snack_bar.content.value = "Debes seleccionar al menos un cartón"
            page.snack_bar.open = True
            page.update()
            return

        detener_polling()
        ids = [int(num) for num in seleccion]
        cantidad = len(ids)
        cartones_str = ",".join(seleccion)
        monto = cantidad * precio_unitario
        numero_orden = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        payload = {
            "cartones_ids": ids,
            "nombre": nombre,
            "telefono": telefono,
            "numero_orden": numero_orden,
            "monto": monto,
            "cantidad_cartones": cantidad,
            "cartones_str": cartones_str
        }

        try:
            supa.rpc("asignar_cartones_temporalmente", payload).execute()
            print("Cartones asignados y orden registrada.")

            # Guardamos la orden para la siguiente pantalla
            page.client_storage.set("orden_actual", {
                "nombre": nombre,
                "telefono": telefono,
                "numero_orden": numero_orden,
                "monto": monto,
                "cantidad_cartones": cantidad,
                "cartones": cartones_str
            })

            page.session_data = {
                "nombre": nombre,
                "telefono": telefono,
                "numero_orden": numero_orden ,
                "monto": monto
            }

            subir_pago(page)

        except Exception as ex:
            print("Error al registrar orden con cartones:", ex)
            page.snack_bar.content.value = "Ocurrió un error al guardar la selección."
            page.snack_bar.open = True
            page.update()

    def cancelar_seleccion(e):
        seleccion.clear()
        lbl_cant.value = "0"
        lbl_precio.value = "0.00 BsD"
        _rebuild_all()
        page.update()

    def volver_a_main(page):
        from main import main_wrapper  # import local para evitar circularidad
        page.controls.clear()
        main_wrapper(page)
        page.update()

    boton_volver = ft.ElevatedButton(
        content=ft.Text(
            "Volver a Inicio",
            size=10,
            color="#ffffff",
            style=ft.TextStyle(font_family="Arial")
        ),
        bgcolor="#711616",
        on_click=lambda e: (
        print("Botón presionado"),
        volver_a_main(page)
        )
    )

    acciones = ft.Row(
        controls=[
            ft.Container(
                content=ft.ElevatedButton(
                    content=ft.Text(
                        "Deseleccionar",
                        size=10,
                        color="#ffffff",
                        style=ft.TextStyle(font_family="Arial")
                    ),
                    bgcolor="#711616",
                    on_click=lambda e: cancelar_seleccion(e)
                ),
                width=page.window_width * 0.3  # 30% del ancho
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    content= ft.Text(
                        "Guardar Selección",
                        size=10,
                        color="#ffffff",
                        style=ft.TextStyle(font_family="Arial")
                    ),
                    bgcolor="#19b01b",
                    on_click=lambda e: guardar_seleccion(e)
                ),
                width=page.window_width * 0.7  # 70% del ancho
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5
    )


    update_toggle_ui() # Llamamos a la función para mostrar la pestaña "Números"

    # 6) Montaje final

    body = ft.Column(
        controls=[
            ft.Row(
                spacing=40
            ),
            encabezado_fila,
            indicadores,
            ft.Container(
                content=header_con_grid,
                width=page.window_width,
                alignment=ft.alignment.center
            ),
            ft.Row(
                spacing=20
            ), 
            acciones,
            ft.Row(
                spacing=20
            ),
            linea_divisoria,
            ft.Row(
                spacing=20
            ),
            ft.Container(
                width=page.window_width,    
                content=  boton_volver),
            ft.Row(
                spacing=40
            )
            ],
            
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
        scroll=ft.ScrollMode.AUTO
    )

    background = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#000000","#101010","#1e1e1e","#343434","#404040","#292929","#121212"]
        ),
        content=body
    )

    page.add(background)
    start_polling()
    page.update()
    