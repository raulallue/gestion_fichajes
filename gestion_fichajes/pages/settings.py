import reflex as rx
from gestion_fichajes.state.state import QueryUser, SettingsState
from gestion_fichajes.components.sidebar import sidebar
from gestion_fichajes.components.navbar import navbar

def settings_page() -> rx.Component:
    return rx.box(
        sidebar(),
        navbar(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.button(
                        rx.icon(tag="arrow-left"),
                        variant="ghost",
                        on_click=lambda: rx.redirect("/"),
                        width=["100%", "auto"],
                    ),
                    rx.heading("Ajustes Globales", size="7", text_align="center"),
                    spacing="3",
                    align_items="center",
                    flex_direction=["column", "row"],
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Festivos Nacionales", weight="bold", size="5"),
                        rx.text("Los días añadidos aquí se aplicarán a toda la empresa. El sistema de fichaje automático se detendrá durante estos días.", size="2", color=rx.color("gray", 11)),
                        rx.divider(margin_y="4"),
                        
                        rx.vstack(
                            rx.vstack(
                                rx.text("Fecha del Festivo", size="2", weight="medium"),
                                rx.input(
                                    type="date", 
                                    value=SettingsState.new_holiday_date, 
                                    on_change=SettingsState.set_new_holiday_date,
                                    variant="soft",
                                    width="100%",
                                ),
                                spacing="1",
                                width=["100%", "100%", "auto"],
                            ),
                            rx.vstack(
                                rx.text("Descripción / Nombre", size="2", weight="medium"),
                                rx.input(
                                    placeholder="Ej: Año Nuevo", 
                                    value=SettingsState.new_holiday_name, 
                                    on_change=SettingsState.set_new_holiday_name,
                                    variant="soft",
                                    width="100%",
                                ),
                                spacing="1",
                                width=["100%", "100%", "auto"],
                            ),
                            rx.button(
                                rx.icon(tag="plus"), "Añadir Festivo", 
                                color_scheme="blue", 
                                on_click=SettingsState.add_holiday,
                                width=["100%", "100%", "auto"],
                            ),
                            spacing="4",
                            align_items="end",
                            width="100%",
                            flex_direction=["column", "column", "row"],
                        ),
                        
                        rx.divider(margin_y="4"),
                        
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Fecha"),
                                    rx.table.column_header_cell("Nombre del Festivo"),
                                    rx.table.column_header_cell("Acciones", justify="end"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    SettingsState.formatted_holidays,
                                    lambda h: rx.table.row(
                                        rx.table.cell(h["date"]),
                                        rx.table.cell(h["name"]),
                                        rx.table.cell(
                                            rx.button(
                                                rx.icon(tag="trash-2", size=16),
                                                variant="ghost",
                                                color_scheme="red",
                                                on_click=lambda: SettingsState.delete_holiday(h["id"])
                                            ),
                                            justify="end"
                                        )
                                    )
                                )
                            ),
                            variant="surface",
                            width="100%",
                        ),
                        rx.cond(
                            SettingsState.formatted_holidays.length() == 0,
                            rx.box(
                                rx.text("No hay festivos configurados.", color=rx.color("gray", 9), text_align="center"),
                                padding="20px",
                                width="100%"
                            )
                        ),
                        width="100%",
                        padding="4",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Configuración del Motor de Fichajes", weight="bold", size="5"),
                        rx.text("Ajusta el realismo de los fichajes automáticos y controla el estado del motor.", size="2", color=rx.color("gray", 11)),
                        rx.divider(margin_y="4"),

                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Margen de Aleatoriedad", size="3", weight="medium"),
                                    rx.text(f"Margen actual: ± {SettingsState.margin_minutes} minutos", size="2", color=rx.color("gray", 10)),
                                    spacing="1",
                                    width="250px",
                                ),
                                rx.slider(
                                    default_value=[5],
                                    value=[SettingsState.margin_minutes],
                                    on_change=SettingsState.set_margin_minutes,
                                    min=0,
                                    max=30,
                                    step=1,
                                    width="100%",
                                ),
                                spacing="6",
                                align_items="center",
                                width="100%",
                            ),
                            rx.divider(margin_y="4"),
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Ejecución Manual", size="3", weight="medium"),
                                    rx.text("Fuerza una iteración del motor ahora mismo para todos los usuarios activos.", size="2", color=rx.color("gray", 10)),
                                    spacing="1",
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon(tag="play"), "Ejecutar Motor Ahora",
                                    color_scheme="blue",
                                    on_click=QueryUser.run_automatic_clock_in,
                                ),
                                width="100%",
                                align_items="center",
                            ),
                            width="100%",
                            spacing="4",
                        ),
                        width="100%",
                        padding="4",
                    ),
                    width="100%",
                    margin_top="6",
                ),
                max_width="1200px",
                width="100%",
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
        spacing="0",
        width="100%",
        on_mount=SettingsState.load_settings,
    )
