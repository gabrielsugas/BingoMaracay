import flet as ft
from view_seleccion import seleccion_cartones
from supabase_client import supa

def verificar_venta_activa(page: ft.Page) -> bool:
    if not consultar_estado_venta():
        pantalla_venta_cerrada(page)
        return False
    return True

def main_wrapper(page: ft.Page):

    def render():
        page.controls.clear()
        if consultar_estado_venta():
            main(page)
        else:
            pantalla_venta_cerrada(page)

    page.on_connect = lambda e: render()
    render()

def consultar_estado_venta():
    try:
        response = supa.table("configuracion").select("valor").eq("clave", "venta_activa").limit(1).execute()
        if response.data and isinstance(response.data, list):
            valor = response.data[0]["valor"]
            return valor == 1 or valor == "1"
    except Exception as e:
        print("Error consultando el estado de la venta:", e)
    return False

def pantalla_venta_cerrada(page: ft.Page):
    page.title = "Bingo Maracay - Cerrado"
    page.window_width = 360
    page.window_height = 640
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.fonts = {
        "BingoFont": "sugo_pro_display/Sugo-Pro-Display-Regular-trial.ttf"
    }

    # Imagen del logo
    logo = ft.Image(
        src="solo_logo.png",
        width=250,
        height=90,
        fit=ft.ImageFit.CONTAIN
    )

    aviso1 = ft.Text(
        "La venta de cartones\nestá pausada por el momento.",
        size=20,
        color="#ff2626",
        text_align=ft.TextAlign.CENTER,
        style=ft.TextStyle(font_family="BingoFont")
    )

    aviso2 = ft.Text(
        "¡Reabriremos\nen unos minutos!",
        size=40,
        color="#fddd58",
        text_align=ft.TextAlign.CENTER,
        style=ft.TextStyle(font_family="BingoFont")
    )

    linea_divisoria = ft.Container(
        height=2,
        width=300,
        bgcolor="#fddd58",
        margin=ft.Margin(0, 1, 0, 1),
    )

    espacio = ft.Row(
        spacing = 5
    )

    # Fondo translúcido por separado (solo visual)
    fondo_translucido = ft.Container(
        bgcolor="#80000000",
        border=ft.border.all(2, "#fddd58"),
        border_radius=12,
        width=350,
        height=400,
        alignment=ft.alignment.center  # Alineamos dentro del Stack
    )

    # Contenido real encima del fondo
    contenido_visible = ft.Container(
        width=600,
        height=400,
        alignment=ft.alignment.center,
        content=ft.Column(
            controls=[
                logo,
                espacio,
                linea_divisoria,
                espacio,
                aviso1,
                aviso2,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # Contenedor para superponer fondo + contenido
    layout = ft.Container(
        content=ft.Stack(
            controls=[
                fondo_translucido,
                contenido_visible
            ],
            expand=True,
            alignment=ft.alignment.center  # Centro del Stack
        ),
        alignment=ft.alignment.center
    )

    fondo = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#000000", "#222222", "#000000"]
        ),
        content=layout
    )

    page.controls.clear()
    page.add(fondo)

def continuar_click(page, input_nombre, input_telefono):
    
    if not verificar_venta_activa(page):
        return
            
    nombre = input_nombre.value.strip()
    telefono = input_telefono.value.strip()

    # Guardamos los placeholders originales
    placeholder_nombre = "Nombre"
    placeholder_telefono = "Teléfono"

    error = False

    # Validar Nombre
    if not nombre:
        input_nombre.value = ""  # para que se muestre el placeholder
        input_nombre.hint_text = "Ingresa tu nombre"
        input_nombre.hint_style = ft.TextStyle(color="#ff2626")
        error = True
    else:
        input_nombre.hint_text = placeholder_nombre
        input_nombre.hint_style = ft.TextStyle(color="#090909")

    # Validar Teléfono
    if not telefono:
        input_telefono.value = ""
        input_telefono.hint_text = "Ingresa tu teléfono"
        input_telefono.hint_style = ft.TextStyle(color="#ff2626")
        error = True
    else:
        input_telefono.hint_text = placeholder_telefono
        input_telefono.hint_style = ft.TextStyle(color="#090909")

    # Si hay error, solo refrescamos y salimos
    if error:
        page.update()
        return

    # Si todo OK, restauramos placeholders y guardamos datos
    input_nombre.hint_text = placeholder_nombre
    input_telefono.hint_text = placeholder_telefono
    page.session_data = {"nombre": nombre, "telefono": telefono}

    # Navegación manual a la siguiente pantalla
    page.controls.clear()
    seleccion_cartones(page)


def volver_inicio(e, page):
    # Vuelve a dibujar la pantalla inicial
    page.controls.clear()
    main(page)
    page.update()

def mostrar_resumen_cartones(page: ft.Page):
    # limpiar y preparar
    page.controls.clear()
    page.snack_bar = ft.SnackBar(content=ft.Text(""), duration=2000)
    page.overlay.append(page.snack_bar)

    # Column que contendrá las líneas
    list_column = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO, expand=True, width=210)
    # Container scrolleable vertical que envuelve la columna
    list_container = ft.Container(
        content=list_column,
        height=420,                # alto del área scrollable
        width=None,
        expand=True,
        padding=ft.padding.all(8),
        bgcolor="#0b0b0b",
        border=ft.border.all(1, "#222222"),
        border_radius=8,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Listado de Cartones", weight="bold", size=18),
        content=ft.Column([
            ft.Text("✅: Verificados - ⚠️: Por Verificar", size=12),
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
        main(page)

    dialog.actions = [
        ft.ElevatedButton("Cerrar", on_click=accion_cerrar, bgcolor="#ff2626"),
    ]

    # abrir modal y cargar datos
    dialog.open = True
    page.update()
    cargar_lista()

def mostrar_modo_de_juego(page: ft.Page):
    # limpiar y preparar (si no quieres limpiar todo, quita/ajusta esta línea)
    page.controls.clear()

    # Column que contendrá las líneas
    list_column = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO, expand=True, width=210)

    # Container scrolleable vertical que envuelve la columna
    list_container = ft.Container(
        content=list_column,
        height=420,
        expand=True,
        padding=ft.padding.all(8),
        bgcolor="#0b0b0b",
        border=ft.border.all(1, "#222222"),
        border_radius=8,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Modo de Juego", weight="bold", size=18),
        content=ft.Column([
            ft.Divider(),
            list_container,
        ], spacing=8),
        actions=[]
    )

    # agregar el dialog al overlay solo si no está ya
    if dialog not in page.overlay:
        page.overlay.append(dialog)

    def cargar_lista(e=None):
        # limpiar controles previos (evita duplicados)
        list_column.controls.clear()

        try:
            res = supa.table("configuracion").select("valor").eq("clave", "modo_de_juego").execute()
        except Exception as ex:
            list_column.controls.append(ft.Text(f"Error consultando configuración: {ex}"))
            list_column.update()
            dialog.update()
            page.update()
            return

        # Obtener el valor de forma segura (asumimos que 'valor' es siempre string)
        contenido = None
        try:
            if hasattr(res, "data"):
                data = res.data
            elif isinstance(res, dict) and "data" in res:
                data = res["data"]
            else:
                data = res

            if isinstance(data, list) and len(data) > 0:
                # primer registro esperado
                first = data[0]
                if isinstance(first, dict) and "valor" in first:
                    contenido = first["valor"]
                else:
                    contenido = first  # fallback
            elif isinstance(data, dict) and "valor" in data:
                contenido = data["valor"]
            else:
                contenido = data  # fallback
        except Exception:
            contenido = None

        # Forzamos a string si no es None
        if contenido is None:
            list_column.controls.append(ft.Text("Sin datos disponibles."))
        else:
            # asegurarnos que sea string
            try:
                contenido_str = str(contenido)
            except Exception:
                contenido_str = ""

            if contenido_str.strip() == "":
                list_column.controls.append(ft.Text("Sin datos disponibles."))
            else:
                # dividir por líneas (splitlines maneja \r\n y \n)
                lines = contenido_str.splitlines()
                # si splitlines devolviera una sola línea con comas y querés separarlas,
                # descomenta la siguiente línea:
                # if len(lines) == 1 and "," in lines[0]: lines = [s.strip() for s in lines[0].split(",") if s.strip()]
                for line in lines:
                    list_column.controls.append(ft.Text(line))

        # refrescar widgets
        list_column.update()
        dialog.update()
        page.update()

    def accion_cerrar(e):
        dialog.open = False
        main(page)


    dialog.actions = [
        ft.ElevatedButton("Cerrar", on_click=accion_cerrar, bgcolor="#ff2626"),
    ]

    # abrir modal y cargar datos
    dialog.open = True
    page.update()
    cargar_lista()

def mostrar_reglamento(page: ft.Page):
    # limpiar y preparar (si no quieres limpiar todo, quita/ajusta esta línea)
    page.controls.clear()

    # Column que contendrá las líneas
    list_column = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO, expand=True, width=210)

    # Container scrolleable vertical que envuelve la columna
    list_container = ft.Container(
        content=list_column,
        height=420,
        expand=True,
        padding=ft.padding.all(8),
        bgcolor="#0b0b0b",
        border=ft.border.all(1, "#222222"),
        border_radius=8,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Reglamento", weight="bold", size=18),
        content=ft.Column([
            ft.Divider(),
            list_container,
        ], spacing=8),
        actions=[]
    )

    # agregar el dialog al overlay solo si no está ya
    if dialog not in page.overlay:
        page.overlay.append(dialog)

    def cargar_lista(e=None):
        # limpiar controles previos (evita duplicados)
        list_column.controls.clear()

        try:
            res = supa.table("configuracion").select("valor").eq("clave", "reglamento").execute()
        except Exception as ex:
            list_column.controls.append(ft.Text(f"Error consultando configuración: {ex}"))
            list_column.update()
            dialog.update()
            page.update()
            return

        # Obtener el valor de forma segura (asumimos que 'valor' es siempre string)
        contenido = None
        try:
            if hasattr(res, "data"):
                data = res.data
            elif isinstance(res, dict) and "data" in res:
                data = res["data"]
            else:
                data = res

            if isinstance(data, list) and len(data) > 0:
                # primer registro esperado
                first = data[0]
                if isinstance(first, dict) and "valor" in first:
                    contenido = first["valor"]
                else:
                    contenido = first  # fallback
            elif isinstance(data, dict) and "valor" in data:
                contenido = data["valor"]
            else:
                contenido = data  # fallback
        except Exception:
            contenido = None

        # Forzamos a string si no es None
        if contenido is None:
            list_column.controls.append(ft.Text("Sin datos disponibles."))
        else:
            # asegurarnos que sea string
            try:
                contenido_str = str(contenido)
            except Exception:
                contenido_str = ""

            if contenido_str.strip() == "":
                list_column.controls.append(ft.Text("Sin datos disponibles."))
            else:
                # dividir por líneas (splitlines maneja \r\n y \n)
                lines = contenido_str.splitlines()
                # si splitlines devolviera una sola línea con comas y querés separarlas,
                # descomenta la siguiente línea:
                # if len(lines) == 1 and "," in lines[0]: lines = [s.strip() for s in lines[0].split(",") if s.strip()]
                for line in lines:
                    list_column.controls.append(ft.Text(line))

        # refrescar widgets
        list_column.update()
        dialog.update()
        page.update()

    def accion_cerrar(e):
        dialog.open = False
        main(page)


    dialog.actions = [
        ft.ElevatedButton("Cerrar", on_click=accion_cerrar, bgcolor="#ff2626"),
    ]

    # abrir modal y cargar datos
    dialog.open = True
    page.update()
    cargar_lista()

def main(page: ft.Page):

    page.fonts = {
        "BingoFont": "sugo_pro_display/Sugo-Pro-Display-Regular-trial.ttf"
    }

    # Configuración básica de la ventana
    page.title = "Bingo Maracay"
    page.window_width = 360
    page.window_height = 640
    page.padding = 0
    # Centramos vertical y horizontalmente
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 1. Creamos los campos de entrada con altura personalizada
    input_nombre = ft.TextField(
        hint_text="Nombre",
        width=300,
        height= 50,       # aquí ajusta a la altura que quieras
        border_radius=6,
        keyboard_type=ft.KeyboardType.TEXT,
        text_style=ft.TextStyle(color="#090909", size=12),
        bgcolor="#FFFFFF",
        focused_border_color="#ff2626"
    )
    input_telefono = ft.TextField(
        hint_text="Teléfono",
        width=300,
        height=50,
        border_radius=6,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color="#090909", size=12),
        bgcolor="#FFFFFF",
        focused_border_color="#ff2626"
    )

    # Fondo translúcido por separado (solo visual)
    fondo_translucido = ft.Container(
        bgcolor="#80000000",
        border=ft.border.all(2, "#fddd58"),
        border_radius=12,
        width=350,
        height=250,
        alignment=ft.alignment.center  # Alineamos dentro del Stack
    )

    # Contenido real encima del fondo
    contenido_visible = ft.Container(
        width=600,
        height=250,
        alignment=ft.alignment.center,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Ingrese sus datos",
                    size=35,
                    color="#fddd58",
                    style=ft.TextStyle(font_family="BingoFont")
                ),
                input_nombre,
                input_telefono,
                ft.ElevatedButton(
                    text="Continuar",
                    width=120,
                    height=40,
                    bgcolor="#ff2626",
                    color="#FFFFFF",
                    on_click=lambda e: continuar_click(page, input_nombre, input_telefono)
                ),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # Contenedor para superponer fondo + contenido
    formulario = ft.Container(
        content=ft.Stack(
            controls=[
                fondo_translucido,
                contenido_visible
            ],
            expand=True,
            alignment=ft.alignment.center  # Centro del Stack
        ),
        alignment=ft.alignment.center
    )

    # Estilo 1 para los botones
    estilo_boton1 = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10),
        bgcolor="#fddd58",
        color="#000000"
    )

    # Botón del Listado
    btn_listado = ft.ElevatedButton(
        text="VER LISTADO COMPLETO",
        width=350,
        height=60,
        style=estilo_boton1,
        on_click=lambda e: mostrar_resumen_cartones(page=page)
    )

    # Estilo 2 para los botones
    estilo_boton2 = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10),
        side=ft.BorderSide(1, "#ffffff"),  # grosor y color del borde
        bgcolor="#ff2626",
        color="#FFFFFF"
    )

    # Botón de Reglamento
    btn_reglamento = ft.ElevatedButton(
        text="REGLAMENTO",
        width=170,
        height=60,
        style=estilo_boton2,
        on_click=lambda e: mostrar_reglamento(page=page)
    )

    # Botón de Modo de Juego
    btn_mododejuego = ft.ElevatedButton(
        text="MODO DE JUEGO",
        width=170,
        height=60,
        style=estilo_boton2,
        on_click=lambda e: mostrar_modo_de_juego(page=page)
    )

    botones_fila = ft.Row(
    controls=[
        btn_reglamento,
        btn_mododejuego
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    spacing=10,  # espacio entre los botones
    )
    
    # Imagen del logo
    logo = ft.Image(
        src="logo.png",
        width=350,
        height=160,
        fit=ft.ImageFit.CONTAIN
    )

    linea_divisoria = ft.Container(
    height=1,
    width=350,
    bgcolor="#fddd58",
    margin=ft.Margin(0, 1, 0, 1),
    )

    # Layout general
    layout = ft.Container(
        alignment=ft.alignment.center,
        content=ft.Column(
            controls=[
                logo,
                formulario,
                btn_listado,
                linea_divisoria,
                botones_fila
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    # 6. Fondo con gradiente que ocupa toda la pantalla
    background = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[
                "#000000",
                "#101010",
                "#1e1e1e",
                "#343434",
                "#404040",
                "#292929",
                "#121212"
            ]
        ),
        content=layout
    )

    page.add(background)


if __name__ == "__main__":
    ft.app(target=main_wrapper, view=ft.WEB_BROWSER, assets_dir=".", host="0.0.0.0", port=5000)
