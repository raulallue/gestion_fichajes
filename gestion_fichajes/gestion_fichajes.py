import reflex as rx
from gestion_fichajes.components.sidebar import sidebar
from gestion_fichajes.components.navbar import navbar
from gestion_fichajes.state.state import QueryUser
from gestion_fichajes.models.model import User

def stat_card(icon: str, label: str, value: str, color: str) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon(tag=icon, size=24, color=rx.color(color, 9)),
                padding="3",
                border_radius="8px",
                bg=rx.color(color, 3),
            ),
            rx.vstack(
                rx.text(label, size="2", color=rx.color("gray", 11)),
                rx.text(value, size="6", weight="bold"),
                spacing="1",
            ),
            spacing="4",
            align_items="center",
        ),
        variant="surface",
        width="100%",
    )

def index() -> rx.Component:
    """Main dashboard page. Adapts stats grid and tables to screen size."""
    return rx.box(
        sidebar(),
        navbar(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.vstack(
                        rx.heading("Dashboard", size="8"),
                        rx.text("Resumen en tiempo real del sistema de control horario.", color=rx.color("gray", 11)),
                        spacing="1",
                        align_items=["center", "center", "start"],
                        text_align=["center", "center", "left"],
                    ),
                    rx.spacer(display=["none", "none", "block"]),
                    # Live clock component
                    rx.card(
                        rx.hstack(
                            rx.icon(tag="clock", color=rx.color("blue", 9)),
                            # Live clock component - Mobile (date + time)
                            rx.moment(
                                format="DD/MM/YYYY - HH:mm:ss",
                                interval=1000,
                                tz="Europe/Madrid",
                                locale="es",
                                display=["block", "block", "none"],
                            ),
                            # Live clock component - Desktop (long format)
                            rx.moment(
                                format="dddd, D [de] MMMM [de] YYYY, HH:mm:ss",
                                interval=1000,
                                tz="Europe/Madrid",
                                locale="es",
                                display=["none", "none", "block"],
                            ),
                            align_items="center",
                            spacing="3",
                        ),
                        variant="surface",
                    ),
                    width="100%",
                    align_items="center",
                    padding_bottom="16px",
                    flex_direction=["column", "column", "row"],
                    spacing="4",
                ),
                
                # Stats grid
                rx.grid(
                    stat_card("users", "Usuarios Totales", QueryUser.dash_total_users, "blue"),
                    rx.card(
                        rx.hstack(
                            rx.box(
                                rx.icon(tag="briefcase", size=24, color=rx.color("green", 9)),
                                padding="3",
                                border_radius="8px",
                                bg=rx.color("green", 3),
                            ),
                            rx.vstack(
                                rx.text("Estado de Hoy", size="2", color=rx.color("gray", 11)),
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(QueryUser.dash_working_now, size="6", weight="bold", color=rx.color("green", 9)),
                                        rx.text("En activo", size="1", color=rx.color("gray", 10)),
                                        spacing="0",
                                        align_items="center",
                                    ),
                                    rx.divider(orientation="vertical", height="30px"),
                                    rx.vstack(
                                        rx.text(QueryUser.dash_finished_today, size="6", weight="bold", color=rx.color("blue", 9)),
                                        rx.text("Finalizado", size="1", color=rx.color("gray", 10)),
                                        spacing="0",
                                        align_items="center",
                                    ),
                                    spacing="4",
                                    align_items="center",
                                ),
                                spacing="1",
                            ),
                            spacing="4",
                            align_items="center",
                        ),
                        variant="surface",
                        width="100%",
                    ),
                    rx.card(
                        rx.hstack(
                            rx.box(
                                rx.icon(tag="sun", size=24, color=rx.color("amber", 9)),
                                padding="3",
                                border_radius="8px",
                                bg=rx.color("amber", 3),
                            ),
                            rx.vstack(
                                rx.text("Ausencias", size="2", color=rx.color("gray", 11)),
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(QueryUser.dash_vacations_today, size="6", weight="bold", color=rx.color("amber", 9)),
                                        rx.text("Vacaciones", size="1", color=rx.color("gray", 10)),
                                        spacing="0",
                                        align_items="center",
                                    ),
                                    rx.divider(orientation="vertical", height="30px"),
                                    rx.vstack(
                                        rx.text(QueryUser.dash_inactive_today, size="6", weight="bold", color=rx.color("tomato", 9)),
                                        rx.text("Inactivos", size="1", color=rx.color("gray", 10)),
                                        spacing="0",
                                        align_items="center",
                                    ),
                                    spacing="4",
                                    align_items="center",
                                ),
                                spacing="1",
                            ),
                            spacing="4",
                            align_items="center",
                        ),
                        variant="surface",
                        width="100%",
                    ),
                    stat_card("calendar", "Fichajes Mensuales", QueryUser.dash_total_monthly_punches, "purple"),
                    columns={"initial": "1", "sm": "2", "lg": "4"},
                    spacing="6",
                    width="100%",
                    padding_bottom="32px",
                ),
                
                rx.vstack(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Últimos Fichajes (Global)", size="4", weight="bold"),
                                rx.spacer(),
                                rx.button(
                                    rx.icon(tag="refresh-cw", size=16),
                                    variant="ghost",
                                    on_click=QueryUser.fetch_dashboard_data,
                                ),
                                width="100%",
                                align_items="center",
                                padding_bottom="4",
                            ),
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Empleado"),
                                            rx.table.column_header_cell("Fecha"),
                                            rx.table.column_header_cell("Entrada"),
                                            rx.table.column_header_cell("Salida"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            QueryUser.dash_recent_punches,
                                            lambda punch: rx.table.row(
                                                rx.table.cell(rx.text(punch["nombre"], weight="medium")),
                                                rx.table.cell(punch["fecha"]),
                                                rx.table.cell(punch["entrada"]),
                                                rx.table.cell(punch["salida"]),
                                            ),
                                        )
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                width="100%",
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="6",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Próximos Turnos", size="4", weight="bold"),
                                rx.spacer(),
                                rx.vstack(
                                    rx.hstack(
                                        rx.checkbox(
                                            on_change=QueryUser.set_show_only_pending,
                                            checked=QueryUser.show_only_pending,
                                            size="1",
                                        ),
                                        rx.text("Solo pendientes", size="1", color_scheme="gray"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            "1h",
                                            on_click=lambda: QueryUser.set_upcoming_window("1"),
                                            variant=rx.cond(QueryUser.upcoming_window == 1, "solid", "outline"),
                                            color_scheme="violet",
                                            size="1",
                                            radius="full",
                                        ),
                                        rx.button(
                                            "3h",
                                            on_click=lambda: QueryUser.set_upcoming_window("3"),
                                            variant=rx.cond(QueryUser.upcoming_window == 3, "solid", "outline"),
                                            color_scheme="violet",
                                            size="1",
                                            radius="full",
                                        ),
                                        rx.button(
                                            "5h",
                                            on_click=lambda: QueryUser.set_upcoming_window("5"),
                                            variant=rx.cond(QueryUser.upcoming_window == 5, "solid", "outline"),
                                            color_scheme="violet",
                                            size="1",
                                            radius="full",
                                        ),
                                        spacing="2",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                width="100%",
                                align_items="center",
                                padding_bottom="4",
                            ),
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Empleado"),
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Hora Prevista"),
                                            rx.table.column_header_cell("Estado"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            QueryUser.dash_upcoming_shifts,
                                            lambda shift: rx.table.row(
                                                rx.table.cell(rx.text(shift["nombre"], weight="medium")),
                                                rx.table.cell(
                                                    rx.badge(
                                                        shift["tipo"],
                                                        color_scheme=rx.cond(shift["tipo"].contains("Entrada"), "green", "blue")
                                                    )
                                                ),
                                                rx.table.cell(rx.text(shift["hora"], weight="bold")),
                                                rx.table.cell(
                                                    rx.badge(
                                                        shift["estado"],
                                                        color_scheme=rx.cond(shift["estado"] == "Completado", "green", "orange"),
                                                        variant="soft",
                                                    )
                                                ),
                                            ),
                                        )
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                width="100%",
                            ),
                            rx.cond(
                                QueryUser.dash_upcoming_shifts.length() == 0,
                                rx.center(
                                    rx.text("No hay turnos próximos en este rango.", color=rx.color("gray", 8), size="2", padding="4"),
                                    width="100%",
                                ),
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="6",
                    ),
                    width="100%",
                    spacing="6",
                    align_items="stretch",
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

from gestion_fichajes.pages.user_details import user_details_page
from gestion_fichajes.pages.vacations_page import vacations_page
from gestion_fichajes.pages.settings import settings_page
from gestion_fichajes.pages.users_page import users_page
from gestion_fichajes.pages.login_page import login_page

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        accent_color="blue",
    ),
    html_lang="es",
)

# --- Server-side Background Startup ---
async def startup_handler():
    """Starts the engine and refresh tasks automatically on server boot."""
    import asyncio
    from gestion_fichajes.services.engine import daemon_loop
    import gestion_fichajes.state.state as state_mod
    
    # Start Clocking Engine
    if not state_mod._ENGINE_STARTED:
        state_mod._ENGINE_STARTED = True
        asyncio.create_task(daemon_loop())
        print("Clocking Engine started automatically on server boot.", flush=True)

app.register_lifespan_task(startup_handler)
app.add_page(login_page, route="/login")
app.add_page(index, on_load=[QueryUser.check_auth, QueryUser.fetch_dashboard_data, QueryUser.check_engine, QueryUser.periodic_refresh])
app.add_page(users_page, route="/usuarios", on_load=[QueryUser.check_auth, QueryUser.cargar_usuarios])
app.add_page(user_details_page, route="/usuario", on_load=[QueryUser.check_auth, QueryUser.check_user_details_access, QueryUser.fetch_history])
app.add_page(vacations_page, route="/vacations", on_load=[QueryUser.check_auth, QueryUser.check_vacations_access])
app.add_page(settings_page, route="/settings", on_load=[QueryUser.check_auth, QueryUser.check_vacations_access])
