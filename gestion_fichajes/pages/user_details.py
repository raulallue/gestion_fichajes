import reflex as rx
from gestion_fichajes.state.state import QueryUser
from gestion_fichajes.components.sidebar import sidebar

def calendar_component() -> rx.Component:
    return rx.vstack(
        # Mes y Navegación
        rx.hstack(
            rx.button(rx.icon(tag="chevron-left"), on_click=QueryUser.prev_month, variant="ghost"),
            rx.heading(QueryUser.calendar_header, size="4", width="150px", text_align="center"),
            rx.button(rx.icon(tag="chevron-right"), on_click=QueryUser.next_month, variant="ghost"),
            justify="center",
            width="100%",
            spacing="4",
            padding_y="2",
        ),
        # Días de la semana
        rx.grid(
            rx.foreach(
                ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                lambda d: rx.text(d, size="1", weight="bold", color=rx.color("gray", 10), text_align="center")
            ),
            columns="7",
            width="100%",
            spacing="1",
        ),
        # Grid de días
        rx.grid(
            rx.foreach(
                QueryUser.calendar_days,
                lambda d: rx.tooltip(
                    rx.box(
                        rx.text(d["day"], size="2", text_align="center"),
                        width="100%",
                        height="35px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                        border_radius="4px",
                        background=rx.cond(
                            d["is_vacation"],
                            rx.color("red", 6),
                            rx.cond(
                                d["is_national_holiday"],
                                rx.color("blue", 7),
                                rx.cond(
                                    d["is_today"],
                                    rx.color("blue", 3),
                                    rx.cond(d["is_empty"], "transparent", rx.color("gray", 2))
                                )
                            )
                        ),
                        color=rx.cond(
                            d["is_vacation"] | d["is_national_holiday"],
                            "white",
                            rx.color("gray", 12)
                        ),
                        border=rx.cond(d["is_today"], f"2px solid {rx.color('blue', 8)}", "none"),
                        opacity=rx.cond(d["is_current_month"], 1.0, 0.4),
                    ),
                    content=d["holiday_name"],
                )
            ),
            columns="7",
            spacing="1",
            width="100%",
        ),
        # Leyenda
        rx.hstack(
            rx.hstack(
                rx.box(width="12px", height="12px", bg=rx.color("red", 6), border_radius="2px"),
                rx.text("Vacaciones", size="1"),
                spacing="1",
                align_items="center",
            ),
            rx.hstack(
                rx.box(width="12px", height="12px", bg=rx.color("blue", 7), border_radius="2px"),
                rx.text("Festivo", size="1"),
                spacing="1",
                align_items="center",
            ),
            rx.hstack(
                rx.box(width="12px", height="12px", border=f"1px solid {rx.color('blue', 8)}", border_radius="2px"),
                rx.text("Hoy", size="1"),
                spacing="1",
                align_items="center",
            ),
            spacing="4",
            padding_top="2",
            width="100%",
            justify="center",
        ),
        width="100%",
        padding="4",
        background=rx.color("gray", 1),
        border_radius="8px",
        border=f"1px solid {rx.color('gray', 4)}",
    )

def manual_fichaje_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Añadir Fichaje Manual"),
                rx.dialog.description("Introduce los datos del fichaje olvidado que se enviará automáticamente a ATR Presencia.", size="2"),
                
                rx.vstack(
                    rx.text("Fecha", size="2", weight="medium"),
                    rx.input(type="date", value=QueryUser.manual_fichaje_date, on_change=QueryUser.set_manual_fichaje_date, width="100%", variant="soft"),
                    spacing="1",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.grid(
                    rx.vstack(
                        rx.text("Entrada", size="2", weight="medium"),
                        rx.input(type="time", value=QueryUser.manual_fichaje_in, on_change=QueryUser.set_manual_fichaje_in, width="100%", variant="soft"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Salida", size="2", weight="medium"),
                        rx.input(type="time", value=QueryUser.manual_fichaje_out, on_change=QueryUser.set_manual_fichaje_out, width="100%", variant="soft"),
                        spacing="1",
                        width="100%",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.vstack(
                    rx.text("Notas (Opcional)", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Ej: Olvido de fichaje, cambio de turno...",
                        value=QueryUser.manual_fichaje_notes,
                        on_change=QueryUser.set_manual_fichaje_notes,
                        width="100%",
                        variant="soft",
                        rows="2",
                    ),
                    spacing="1",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        color_scheme="gray",
                        variant="soft",
                        on_click=QueryUser.toggle_manual_dialog,
                    ),
                    rx.button(
                        "Enviar Fichaje a ATR",
                        color_scheme="blue",
                        on_click=QueryUser.add_manual_fichaje,
                    ),
                    spacing="3",
                    margin_top="6",
                    justify="end",
                    width="100%",
                ),
            ),
            max_width="450px",
        ),
        open=QueryUser.show_manual_dialog,
    )

def edit_fichaje_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Editar Fichaje"),
                rx.dialog.description("Modifica la hora de entrada/salida para cerrar o corregir el registro en ATR Presencia.", size="2"),
                
                rx.vstack(
                    rx.text("Fecha", size="2", weight="medium"),
                    rx.input(type="date", value=QueryUser.edit_fichaje_date, on_change=QueryUser.set_edit_fichaje_date, width="100%", variant="soft"),
                    spacing="1",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.grid(
                    rx.vstack(
                        rx.text("Entrada", size="2", weight="medium"),
                        rx.input(type="time", value=QueryUser.edit_fichaje_in, on_change=QueryUser.set_edit_fichaje_in, width="100%", variant="soft"),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Salida", size="2", weight="medium"),
                        rx.input(type="time", value=QueryUser.edit_fichaje_out, on_change=QueryUser.set_edit_fichaje_out, width="100%", variant="soft"),
                        spacing="1",
                        width="100%",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.vstack(
                    rx.text("Notas", size="2", weight="medium"),
                    rx.text_area(
                        placeholder="Edita las notas del fichaje...",
                        value=QueryUser.edit_fichaje_notes,
                        on_change=QueryUser.set_edit_fichaje_notes,
                        width="100%",
                        variant="soft",
                        rows="2",
                    ),
                    spacing="1",
                    width="100%",
                    margin_top="2",
                ),
                
                rx.hstack(
                    rx.button(
                        "Cancelar",
                        color_scheme="gray",
                        variant="soft",
                        on_click=QueryUser.toggle_edit_dialog,
                    ),
                    rx.button(
                        "Guardar Cambios",
                        color_scheme="blue",
                        on_click=QueryUser.update_manual_fichaje,
                    ),
                    spacing="3",
                    margin_top="6",
                    justify="end",
                    width="100%",
                ),
            ),
            max_width="450px",
        ),
        open=QueryUser.show_edit_dialog,
    )

def user_details_page() -> rx.Component:
    return rx.hstack(
        sidebar(),
        manual_fichaje_dialog(),
        edit_fichaje_dialog(),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.button(
                        rx.icon(tag="arrow-left"),
                        variant="ghost",
                        on_click=lambda: rx.redirect("/usuarios"),
                    ),
                    rx.heading(
                        rx.cond(QueryUser.user_edit_id, "Editar Usuario", "Añadir Nuevo Usuario"),
                        size="7"
                    ),
                    spacing="3",
                    align_items="center",
                ),
                
                rx.card(
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Perfil", value="perfil"),
                            rx.tabs.trigger("Horarios", value="horarios"),
                            rx.cond(QueryUser.user_edit_id, rx.tabs.trigger("Vacaciones", value="vacaciones")),
                            rx.cond(QueryUser.user_edit_id, rx.tabs.trigger("Últimos Fichajes", value="historial")),
                            width="100%",
                        ),
                        
                        # CONTENIDO: PERFIL
                        rx.tabs.content(
                            rx.vstack(
                                rx.text("Datos del Perfil", weight="bold", size="3"),
                                rx.vstack(
                                    rx.text("Nombre Completo", size="2", weight="medium"),
                                    rx.input(placeholder="Ej: Raúl Allué", value=QueryUser.nuevo_nombre, on_change=QueryUser.set_nuevo_nombre, width="100%", variant="soft"),
                                    spacing="1",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.switch(checked=QueryUser.nuevo_activo, on_change=QueryUser.set_nuevo_activo),
                                    rx.text("Usuario Activo (realizará fichajes automáticos)", size="2"),
                                    align_items="center", spacing="2", margin_y="1",
                                ),
                                rx.cond(
                                    QueryUser.user_edit_id,
                                    rx.vstack(
                                        rx.text("ID Persona (ATR)", size="2", weight="medium"),
                                        rx.input(value=QueryUser.nuevo_person_id, is_disabled=True, width="100%", variant="soft"),
                                        spacing="1",
                                        width="100%",
                                    ),
                                ),
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Usuario ATR", size="2", weight="medium"),
                                        rx.input(placeholder="usuario@dominio", value=QueryUser.nuevo_usuario, on_change=QueryUser.set_nuevo_usuario, width="100%", variant="soft"),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("Contraseña ATR", size="2", weight="medium"),
                                        rx.input(
                                            rx.input.slot(
                                                rx.icon(
                                                    tag=rx.cond(QueryUser.show_password, "eye-off", "eye"),
                                                    on_click=QueryUser.toggle_show_password,
                                                    cursor="pointer",
                                                    size=14,
                                                    color=rx.color("gray", 9),
                                                ),
                                            ),
                                            type=rx.cond(QueryUser.show_password, "text", "password"),
                                            placeholder="********",
                                            value=QueryUser.nuevo_contraseña,
                                            on_change=QueryUser.set_nuevo_contraseña,
                                            width="100%",
                                            variant="soft",
                                        ),
                                        spacing="1",
                                    ),
                                    columns="2",
                                    spacing="4",
                                    width="100%",
                                ),
                                rx.cond(
                                    QueryUser.is_admin,
                                    rx.vstack(
                                        rx.text("Rol en el Sistema", size="2", weight="medium"),
                                        rx.select(
                                            {"user": "Usuario Estándar", "admin": "Administrador"},
                                            value=QueryUser.nuevo_rol,
                                            on_change=QueryUser.set_nuevo_rol,
                                            width="100%",
                                            variant="soft",
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                ),
                                spacing="4",
                                padding_y="4",
                                margin_top="10px",
                            ),
                            value="perfil",
                        ),
                        
                        # CONTENIDO: HORARIOS
                        rx.tabs.content(
                            rx.vstack(
                                rx.text("Configuración de Jornada", weight="bold", size="3"),
                                rx.grid(
                                    rx.vstack(
                                        rx.text("Entrada Mañana", size="2", weight="medium"),
                                        rx.input(type="time", value=QueryUser.nuevo_chin_1, on_change=QueryUser.set_nuevo_chin_1, width="100%", variant="soft"),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("Salida Mañana", size="2", weight="medium"),
                                        rx.input(type="time", value=QueryUser.nuevo_chout_1, on_change=QueryUser.set_nuevo_chout_1, width="100%", variant="soft"),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("Entrada Tarde", size="2", weight="medium"),
                                        rx.input(type="time", value=QueryUser.nuevo_chin_2, on_change=QueryUser.set_nuevo_chin_2, width="100%", variant="soft", disabled=QueryUser.nuevo_intensiva),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("Salida Tarde", size="2", weight="medium"),
                                        rx.input(type="time", value=QueryUser.nuevo_chout_2, on_change=QueryUser.set_nuevo_chout_2, width="100%", variant="soft", disabled=QueryUser.nuevo_intensiva),
                                        spacing="1",
                                    ),
                                    columns="2",
                                    spacing="4",
                                    width="100%",
                                ),
                                rx.divider(),
                                rx.hstack(
                                    rx.text("Jornada Intensiva", weight="medium"),
                                    rx.switch(checked=QueryUser.nuevo_intensiva, on_change=QueryUser.set_nuevo_intensiva),
                                    spacing="4",
                                    align_items="center",
                                ),
                                rx.divider(),
                                rx.vstack(
                                    rx.text("Días de Trabajo", weight="medium"),
                                    rx.hstack(
                                        rx.foreach(
                                            [0, 1, 2, 3, 4, 5, 6],
                                            lambda day: rx.button(
                                                rx.cond(day == 0, "L", rx.cond(day == 1, "M", rx.cond(day == 2, "X", rx.cond(day == 3, "J", rx.cond(day == 4, "V", rx.cond(day == 5, "S", "D")))))),
                                                on_click=lambda: QueryUser.toggle_work_day(day),
                                                color_scheme=rx.cond(QueryUser.nuevo_work_days.contains(day), "blue", "gray"),
                                                variant=rx.cond(QueryUser.nuevo_work_days.contains(day), "solid", "soft"),
                                                size="2",
                                            )
                                        ),
                                        spacing="2",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                    width="100%",
                                ),
                                
                                # Zona de Depuración (Debug)
                                rx.divider(margin_y="4"),
                                rx.card(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("bug", size=20, color=rx.color("amber", 9)),
                                            rx.text("Zona de Pruebas (Debug)", weight="bold", size="3"),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.text(
                                            "Si cambias el horario y quieres que el motor vuelva a fichar hoy, pulsa el botón de abajo para 'olvidar' que ya se fichó.",
                                            size="2",
                                            color_scheme="gray",
                                        ),
                                        rx.button(
                                            "Resetear Automatización de Hoy",
                                            icon="refresh-cw",
                                            color_scheme="amber",
                                            variant="surface",
                                            size="2",
                                            align_self="center",
                                            on_click=QueryUser.reset_auto_flags,
                                            px="6",
                                            py="3",
                                        ),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    width="100%",
                                    variant="classic",
                                    color_scheme="amber",
                                    padding="6",
                                ),
                                
                                spacing="4",
                                padding_y="4",
                                margin_top="10px",
                            ),
                            value="horarios",
                        ),
                        
                        # CONTENIDO: VACACIONES
                        rx.tabs.content(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Gestión Visual de Vacaciones", weight="bold", size="3"),
                                    rx.spacer(),
                                    rx.badge(
                                        rx.icon(tag="calendar-check", size=14),
                                        f"Total: {QueryUser.total_vacation_days} días",
                                        color_scheme="blue",
                                        variant="outline",
                                    ),
                                    rx.badge(
                                        rx.icon(tag="coffee", size=14),
                                        f"Sáb/Dom: {QueryUser.weekend_vacation_days} días",
                                        color_scheme="orange",
                                        variant="outline",
                                    ),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.grid(
                                    rx.vstack(
                                        calendar_component(),
                                        spacing="4",
                                        width="100%",
                                    ),
                                    rx.vstack(
                                        rx.text("Añadir Periodo", weight="bold", size="2"),
                                        rx.grid(
                                            rx.vstack(
                                                rx.text("Inicio", size="1"),
                                                rx.input(type="date", value=QueryUser.nueva_fecha_vacacion, on_change=QueryUser.set_nueva_fecha_vacacion, width="100%", variant="soft"),
                                                spacing="1",
                                            ),
                                            rx.vstack(
                                                rx.text("Fin", size="1"),
                                                rx.input(type="date", value=QueryUser.nueva_fecha_fin, on_change=QueryUser.set_nueva_fecha_fin, width="100%", variant="soft"),
                                                spacing="1",
                                            ),
                                            columns="2",
                                            spacing="3",
                                            width="100%",
                                        ),
                                        rx.button(
                                            rx.icon(tag="plus"),
                                            "Añadir Días",
                                            on_click=QueryUser.add_vacation_day,
                                            width="100%",
                                            color_scheme="blue",
                                        ),
                                        rx.divider(margin_y="10px"),
                                        rx.text("Listado de Días", size="2", weight="bold"),
                                        rx.scroll_area(
                                            rx.vstack(
                                                rx.foreach(
                                                    QueryUser.formatted_vacaciones,
                                                    lambda v: rx.hstack(
                                                        rx.text(v["date"], size="2"),
                                                        rx.spacer(),
                                                        rx.button(
                                                            rx.icon(tag="trash-2", size=12),
                                                            on_click=lambda: QueryUser.delete_vacation_day(v["id"]),
                                                            variant="ghost",
                                                            color_scheme="red",
                                                            size="1",
                                                        ),
                                                        width="100%",
                                                        padding_y="1",
                                                        padding_right="12px",
                                                        border_bottom=f"1px solid {rx.color('gray', 4)}",
                                                    )
                                                ),
                                                width="100%",
                                            ),
                                            style={"height": "130px"},
                                        ),
                                        spacing="3",
                                        width="100%",
                                        padding="4",
                                        background=rx.color("blue", 2),
                                        border_radius="8px",
                                    ),
                                    columns="2",
                                    spacing="6",
                                    width="100%",
                                ),
                                spacing="4",
                                padding_y="4",
                                margin_top="10px",
                            ),
                            value="vacaciones",
                        ),
                        
                        # CONTENIDO: HISTORIAL
                        rx.tabs.content(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Historial de Fichajes (ATR)", weight="bold", size="3"),
                                    rx.spacer(),
                                    rx.button(
                                        rx.icon(tag="plus", size=16),
                                        "Fichaje Manual",
                                        on_click=QueryUser.toggle_manual_dialog,
                                        variant="outline",
                                        color_scheme="blue",
                                    ),
                                    rx.select(
                                        ["7", "15", "30", "90"],
                                        placeholder="Rango de días",
                                        value=QueryUser.history_range,
                                        on_change=QueryUser.change_history_range,
                                        width="150px",
                                        variant="soft",
                                    ),
                                    width="100%",
                                    align_items="center",
                                ),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell(
                                                rx.hstack(
                                                    rx.text("Fecha"),
                                                    rx.icon(
                                                        tag=rx.cond(QueryUser.history_sort_key == "fecha", rx.cond(QueryUser.history_sort_asc, "arrow-up", "arrow-down"), "chevrons-up-down"),
                                                        size=13,
                                                    ),
                                                    cursor="pointer",
                                                    on_click=lambda: QueryUser.sort_history("fecha"),
                                                    spacing="1",
                                                    align_items="center",
                                                )
                                            ),
                                            rx.table.column_header_cell(
                                                rx.hstack(
                                                    rx.text("Entrada"),
                                                    rx.icon(
                                                        tag=rx.cond(QueryUser.history_sort_key == "entrada", rx.cond(QueryUser.history_sort_asc, "arrow-up", "arrow-down"), "chevrons-up-down"),
                                                        size=13,
                                                    ),
                                                    cursor="pointer",
                                                    on_click=lambda: QueryUser.sort_history("entrada"),
                                                    spacing="1",
                                                    align_items="center",
                                                )
                                            ),
                                            rx.table.column_header_cell("Salida"),
                                            rx.table.column_header_cell("Notas"),
                                            rx.table.column_header_cell("", width="50px"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            QueryUser.history_fichajes,
                                            lambda h: rx.table.row(
                                                rx.table.cell(h["fecha"]),
                                                rx.table.cell(h["entrada"]),
                                                rx.table.cell(h["salida"]),
                                                rx.table.cell(h["notas"], size="1"),
                                                rx.table.cell(
                                                    rx.button(
                                                        rx.icon(tag="pencil", size=14),
                                                        variant="ghost",
                                                        color_scheme="gray",
                                                        on_click=lambda: QueryUser.open_edit_dialog(h["id"]),
                                                    ),
                                                    padding="2px",
                                                    display="flex",
                                                    align_items="center",
                                                ),
                                                align_items="center",
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                rx.cond(
                                    QueryUser.history_fichajes.length() == 0,
                                    rx.vstack(
                                        rx.text("No se encontraron fichajes en este rango.", color=rx.color("gray", 9)),
                                        rx.button("Reintentar", on_click=QueryUser.fetch_history, variant="ghost", size="1"),
                                        width="100%",
                                        spacing="2",
                                        padding="8",
                                    ),
                                ),
                                spacing="4",
                                padding_y="4",
                                margin_top="10px",
                            ),
                            value="historial",
                        ),
                        
                        on_change=QueryUser.handle_tab_change,
                        value=QueryUser.active_tab,
                        width="100%",
                    ),
                    width="100%",
                    padding="20px",
                ),
                
                rx.hstack(
                    rx.button(
                        "Volver a Usuarios",
                        color_scheme="gray",
                        variant="soft",
                        on_click=lambda: rx.redirect("/usuarios"),
                    ),
                    rx.cond(
                        QueryUser.active_tab != "historial",
                        rx.button(
                            rx.cond(QueryUser.user_edit_id, "Guardar Cambios", "Crear Usuario"),
                            on_click=rx.cond(QueryUser.user_edit_id, QueryUser.update_user, QueryUser.add_user),
                            color_scheme="blue",
                        )
                    ),
                    width="100%",
                    justify="end",
                    spacing="3",
                    padding_top="20px",
                ),

                max_width="1200px",
                width="100%",
                margin="0 auto",
                padding="40px",
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
