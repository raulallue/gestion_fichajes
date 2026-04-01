import reflex as rx
from gestion_fichajes.components.sidebar import sidebar
from gestion_fichajes.components.navbar import navbar
from gestion_fichajes.state.state import QueryUser

def day_selector() -> rx.Component:
    """Días de la semana selector inline."""
    day_labels = ["L", "M", "X", "J", "V", "S", "D"]
    return rx.hstack(
        *[
            rx.button(
                day_labels[i],
                size="1",
                variant=rx.cond(
                    QueryUser.nuevo_work_days.contains(i),
                    "solid",
                    "outline"
                ),
                on_click=lambda d=i: QueryUser.toggle_work_day(d),
            )
            for i in range(7)
        ],
        spacing="1",
    )

def add_user_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Añadir Nuevo Usuario"),
                rx.dialog.description("Rellena los datos del nuevo empleado, incluidas las credenciales ATR Presencia.", size="2"),

                rx.grid(
                    rx.vstack(
                        rx.text("Nombre Completo", size="2", weight="medium"),
                        rx.input(placeholder="Ej: Juan García", value=QueryUser.nuevo_nombre, on_change=QueryUser.set_nuevo_nombre, width="100%", variant="soft"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Usuario ATR", size="2", weight="medium"),
                        rx.input(placeholder="Ej: juan@empresa", value=QueryUser.nuevo_usuario, on_change=QueryUser.set_nuevo_usuario, width="100%", variant="soft"),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="4", width="100%",
                ),

                rx.hstack(
                    rx.switch(checked=QueryUser.nuevo_activo, on_change=QueryUser.set_nuevo_activo),
                    rx.text("Usuario Activo (realizará fichajes automáticos)", size="2"),
                    align_items="center", spacing="2", margin_y="1",
                ),

                rx.vstack(
                    rx.text("Contraseña ATR", size="2", weight="medium"),
                    rx.input(type="password", placeholder="Contraseña ATR", value=QueryUser.nuevo_contraseña, on_change=QueryUser.set_nuevo_contraseña, width="100%", variant="soft"),
                    spacing="1", width="100%",
                ),

                rx.divider(margin_y="2"),
                rx.text("Horario Jornada 1", size="2", weight="bold"),
                rx.grid(
                    rx.vstack(
                        rx.text("Entrada", size="2"),
                        rx.input(type="time", value=QueryUser.nuevo_chin_1, on_change=QueryUser.set_nuevo_chin_1, width="100%", variant="soft"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Salida", size="2"),
                        rx.input(type="time", value=QueryUser.nuevo_chout_1, on_change=QueryUser.set_nuevo_chout_1, width="100%", variant="soft"),
                        spacing="1", width="100%",
                    ),
                    columns="2", spacing="4", width="100%",
                ),

                rx.hstack(
                    rx.switch(checked=QueryUser.nuevo_intensiva, on_change=QueryUser.set_nuevo_intensiva),
                    rx.text("Jornada Intensiva (sin jornada 2)", size="2"),
                    align_items="center", spacing="2", margin_y="2",
                ),

                rx.cond(
                    ~QueryUser.nuevo_intensiva,
                    rx.vstack(
                        rx.text("Horario Jornada 2", size="2", weight="bold"),
                        rx.grid(
                            rx.vstack(
                                rx.text("Entrada", size="2"),
                                rx.input(type="time", value=QueryUser.nuevo_chin_2, on_change=QueryUser.set_nuevo_chin_2, width="100%", variant="soft"),
                                spacing="1", width="100%",
                            ),
                            rx.vstack(
                                rx.text("Salida", size="2"),
                                rx.input(type="time", value=QueryUser.nuevo_chout_2, on_change=QueryUser.set_nuevo_chout_2, width="100%", variant="soft"),
                                spacing="1", width="100%",
                            ),
                            columns="2", spacing="4", width="100%",
                        ),
                        width="100%",
                        spacing="2",
                    ),
                ),

                rx.hstack(
                    rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=QueryUser.toggle_add_user_modal),
                    rx.button(
                        rx.icon(tag="user-plus", size=16),
                        "Crear Usuario",
                        color_scheme="blue",
                        on_click=QueryUser.add_user,
                    ),
                    spacing="3",
                    justify="end",
                    width="100%",
                    margin_top="4",
                ),

                spacing="4",
                width="100%",
            ),
            max_width="560px",
            overflow_y="auto",
            max_height="90vh",
        ),
        open=QueryUser.show_add_user_modal,
    )


def delete_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Confirmar Eliminación"),
                rx.dialog.description(
                    rx.text("Esta acción no se puede deshacer. Para confirmar, escribe el nombre de usuario de ATR (", weight="light", as_="span"),
                    rx.text(QueryUser.delete_confirm_user_username, weight="bold", color_scheme="red", as_="span"),
                    rx.text(") a continuación:", weight="light", as_="span"),
                    size="2",
                ),
                rx.input(
                    placeholder="Escribe el usuario aquí...",
                    value=QueryUser.delete_confirm_input,
                    on_change=QueryUser.set_delete_confirm_input,
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=QueryUser.close_delete_dialog)
                    ),
                    rx.button(
                        "Eliminar Permanentemente",
                        color_scheme="red",
                        on_click=QueryUser.delete_user,
                        disabled=QueryUser.delete_confirm_input != QueryUser.delete_confirm_user_username,
                    ),
                    width="100%",
                    justify="end",
                    spacing="3",
                ),
                spacing="4",
            ),
            max_width="450px",
        ),
        open=QueryUser.show_confirm_dialog,
    )

def users_page() -> rx.Component:
    """User management page. Stacks controls on mobile and adds horizontal scrolling to the data table."""
    return rx.box(
        sidebar(),
        navbar(),
        add_user_modal(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.vstack(
                        rx.heading("Gestión de Usuarios", size="8"),
                        rx.text("Administra la plantilla, activa vacaciones y modifica credenciales.", color=rx.color("gray", 11)),
                        spacing="1",
                        align_items=["center", "center", "start"],
                        text_align=["center", "center", "left"],
                    ),
                    rx.spacer(display=["none", "none", "block"]),
                    rx.cond(
                        QueryUser.is_admin,
                        rx.button(
                            rx.icon(tag="user-plus"),
                            "Nuevo Usuario",
                            on_click=QueryUser.toggle_add_user_modal,
                            color_scheme="blue",
                            width=["100%", "100%", "auto"],
                        ),
                    ),
                    width="100%",
                    align_items="center",
                    padding_bottom="16px",
                    flex_direction=["column", "column", "row"],
                    spacing="4",
                ),
                
                # Buscador y Diálogos
                delete_dialog(),
                rx.vstack(
                    rx.input(
                        rx.input.slot(rx.icon(tag="search")),
                        placeholder="Buscar por nombre o usuario...",
                        value=QueryUser.search_value,
                        on_change=QueryUser.set_search_value,
                        width="100%",
                        max_width=["100%", "100%", "400px"],
                        variant="soft",
                    ),
                    rx.spacer(display=["none", "none", "block"]),
                    padding_bottom="16px",
                    width="100%",
                    align_items="center",
                    flex_direction=["column", "column", "row"],
                ),

                # Tabla de Usuarios
                rx.card(
                    rx.scroll_area(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Usuario"),
                                    rx.table.column_header_cell("ATR User"),
                                    rx.table.column_header_cell("Jornada 1"),
                                    rx.table.column_header_cell("Jornada 2 / Tipo"),
                                    rx.table.column_header_cell("Días"),
                                    rx.table.column_header_cell("Estado"),
                                    rx.table.column_header_cell("Acciones", align="right"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    QueryUser.filtered_users_with_status,
                                    lambda item: rx.table.row(
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.avatar(fallback=item[0].nombre[0].upper(), size="1"),
                                                rx.text(item[0].nombre, weight="medium"),
                                                align_items="center",
                                                spacing="2",
                                            )
                                        ),
                                        rx.table.cell(rx.code(item[0].usuario)),
                                        rx.table.cell(f"{item[0].chin_1} - {item[0].chout_1}"),
                                        rx.table.cell(
                                            rx.cond(
                                                item[0].intensiva,
                                                rx.badge("Intensiva", color_scheme="green", variant="surface"),
                                                rx.text(f"{item[0].chin_2} - {item[0].chout_2}", size="2")
                                            )
                                        ),
                                        rx.table.cell(rx.text(item[2], size="2", color=rx.color("gray", 11))),
                                        rx.table.cell(
                                            rx.cond(
                                                ~item[0].activo,
                                                rx.badge("Inactivo", color_scheme="gray", variant="solid"),
                                                rx.badge(
                                                    rx.cond(item[1], "Vacaciones", "Activo"),
                                                    color_scheme=rx.cond(item[1], "amber", "grass"),
                                                    variant="soft",
                                                ),
                                            ),
                                        ),
                                        rx.table.cell(
                                            rx.hstack(
                                                rx.tooltip(
                                                    rx.button(
                                                        rx.icon(tag="clock", size=14),
                                                        on_click=lambda: QueryUser.cargar_usuario_historial(item[0].id),
                                                        variant="ghost",
                                                        color_scheme="purple",
                                                        size="1",
                                                    ),
                                                    content="Ver Fichajes",
                                                ),
                                                rx.tooltip(
                                                    rx.button(
                                                        rx.icon(tag="pencil", size=14),
                                                        on_click=lambda: QueryUser.cargar_usuario_para_editar(item[0].id),
                                                        variant="ghost",
                                                        size="1",
                                                    ),
                                                    content="Editar Usuario",
                                                ),
                                                rx.cond(
                                                    QueryUser.is_admin,
                                                    rx.tooltip(
                                                        rx.button(
                                                            rx.icon(tag="trash-2", size=14),
                                                            on_click=lambda: QueryUser.open_delete_dialog(item[0].id, item[0].usuario),
                                                            variant="ghost",
                                                            color_scheme="red",
                                                            size="1",
                                                        ),
                                                        content="Eliminar",
                                                    ),
                                                ),
                                                justify="end",
                                                spacing="2",
                                            )
                                        ),
                                        align_items="center",
                                    )
                                )
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        width="100%",
                    ),
                    width="100%",
                    padding="0",
                ),
                
                width="100%",
                max_width="1200px",
                margin="0 auto",
                padding=["20px", "20px", "40px"],
                padding_top=["80px", "80px", "40px"],
            ),
            flex="1",
            margin_left=["0", "0", rx.cond(QueryUser.sidebar_collapsed, "64px", "280px")],
            bg=rx.color("gray", 1),
            min_height="100vh",
            transition="margin-left 0.3s ease",
        ),
        width="100%",
        spacing="0",
    )
