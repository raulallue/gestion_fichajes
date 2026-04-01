import reflex as rx
from gestion_fichajes.state.state import QueryUser
from gestion_fichajes.components.sidebar import sidebar
from gestion_fichajes.components.navbar import navbar
from gestion_fichajes.models.model import User

def vacations_page() -> rx.Component:
    """Vacation calendar page. Stacks the selection card and the listing card verticaly on mobile."""
    return rx.box(
        sidebar(),
        navbar(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.heading("Calendario de Vacaciones", size="8"),
                    rx.text("Registra y gestiona los periodos de ausencia de la plantilla.", color=rx.color("gray", 11)),
                    spacing="1",
                    align_items=["center", "center", "start"],
                    text_align=["center", "center", "left"],
                    padding_bottom="24px",
                ),
                
                rx.grid(
                    # Columna Izquierda: Selección de Usuario y Añadir Fecha
                    rx.card(
                        rx.vstack(
                            rx.text("1. Selecciona un Usuario", weight="bold", size="3"),
                            rx.select(
                                QueryUser.nombre_usuarios,
                                placeholder="Selecciona un usuario...",
                                on_change=QueryUser.seleccionar_usuario_por_nombre,
                                width="100%",
                                variant="soft",
                            ),
                            
                            rx.divider(margin_y="12px"),
                            
                            rx.text("2. Rango de Vacaciones", weight="bold", size="3"),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Inicio", size="1", color=rx.color("gray", 11)),
                                    rx.input(
                                        type="date",
                                        value=QueryUser.nueva_fecha_vacacion,
                                        on_change=QueryUser.set_nueva_fecha_vacacion,
                                        width="100%",
                                        variant="soft",
                                    ),
                                    width="100%",
                                    spacing="1",
                                ),
                                rx.vstack(
                                    rx.text("Fin (Opcional)", size="1", color=rx.color("gray", 11)),
                                    rx.input(
                                        type="date",
                                        value=QueryUser.nueva_fecha_fin,
                                        on_change=QueryUser.set_nueva_fecha_fin,
                                        width="100%",
                                        variant="soft",
                                    ),
                                    width="100%",
                                    spacing="1",
                                ),
                                width="100%",
                                spacing="3",
                            ),
                            rx.button(
                                rx.icon(tag="calendar-plus"),
                                "Añadir Periodo",
                                on_click=QueryUser.add_vacation_day,
                                width="100%",
                                margin_top="12px",
                                color_scheme="blue",
                            ),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    
                    # Columna Derecha: Lista de Vacaciones Registradas
                    rx.card(
                        rx.vstack(
                            rx.text("Días Registrados", weight="bold", size="3"),
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Fecha"),
                                        rx.table.column_header_cell("Acciones"),
                                    ),
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        QueryUser.formatted_vacaciones,
                                        lambda v: rx.table.row(
                                            rx.table.cell(v["date"]),
                                            rx.table.cell(
                                                rx.button(
                                                    rx.icon(tag="trash-2", size=14),
                                                    on_click=lambda: QueryUser.delete_vacation_day(v["id"]),
                                                    variant="ghost",
                                                    color_scheme="red",
                                                    size="1",
                                                )
                                            ),
                                        ),
                                    ),
                                ),
                                width="100%",
                            ),
                            rx.cond(
                                QueryUser.formatted_vacaciones.length() == 0,
                                rx.text("No hay vacaciones registradas para este usuario.", size="2", color=rx.color("gray", 9)),
                            ),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    columns={"initial": "1", "lg": "2"},
                    spacing="6",
                    width="100%",
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
