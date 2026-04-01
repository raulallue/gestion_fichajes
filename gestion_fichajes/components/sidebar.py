import reflex as rx
from gestion_fichajes.state.state import QueryUser

def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(tag=icon, size=24),
            rx.cond(
                ~QueryUser.sidebar_collapsed,
                rx.text(text, size="3"),
            ),
            spacing="3",
            align_items="center",
            justify_content=rx.cond(QueryUser.sidebar_collapsed, "center", "start"),
            padding_x=rx.cond(QueryUser.sidebar_collapsed, "0px", "12px"),
            padding_y="10px",
            border_radius="lg",
            _hover={
                "bg": rx.color("accent", 3),
                "color": rx.color("accent", 11),
            },
            color=rx.color("gray", 11),
            transition="all 0.2s",
            width="100%",
        ),
        href=url,
        text_decoration="none",
        width="100%",
    )

def sidebar() -> rx.Component:
    """Fixed sidebar for desktop and sliding drawer for mobile/tablet."""
    return rx.box(
        rx.vstack(
            # Header con Logo y Toggle
            rx.hstack(
                rx.cond(
                    ~QueryUser.sidebar_collapsed,
                    rx.hstack(
                        rx.image(src="/logo.png", width="32px", height="auto", border_radius="4px"),
                        rx.heading("AutoFichaje", size="6", weight="bold"),
                        spacing="3",
                        align_items="center",
                        flex_shrink="0",
                    ),
                    rx.fragment(),
                ),
                rx.spacer(display=rx.cond(QueryUser.sidebar_collapsed, "none", "block")),
                rx.icon(
                    tag="menu",
                    size=22,
                    cursor="pointer",
                    on_click=QueryUser.toggle_sidebar,
                    color=rx.color("gray", 9),
                    _hover={"color": rx.color("accent", 9)},
                    flex_shrink="0",
                    display=["none", "none", "block"],
                ),
                # Botón de cerrar para móvil
                rx.icon(
                    tag="x",
                    size=22,
                    cursor="pointer",
                    on_click=QueryUser.toggle_mobile_sidebar,
                    color=rx.color("gray", 9),
                    display=["block", "block", "none"],
                ),
                width="100%",
                padding_x=rx.cond(QueryUser.sidebar_collapsed, "0px", "12px"),
                margin_bottom="32px",
                align_items="center",
                justify_content=rx.cond(QueryUser.sidebar_collapsed, "center", "space-between"),
            ),
            # Items del Menú
            rx.vstack(
                sidebar_item("Panel de Control", "layout-dashboard", "/"),
                sidebar_item("Usuarios", "users", "/usuarios"),
                rx.cond(
                    QueryUser.is_admin,
                    sidebar_item("Vacaciones", "calendar", "/vacations"),
                ),
                rx.cond(
                    QueryUser.is_admin,
                    sidebar_item("Ajustes", "settings", "/settings"),
                ),
                spacing="1",
                width="100%",
                align_items=rx.cond(QueryUser.sidebar_collapsed, "center", "stretch"),
            ),
            rx.spacer(),
            # Perfil de Usuario
            rx.cond(
                QueryUser.is_authenticated,
                rx.box(
                    rx.cond(
                        ~QueryUser.sidebar_collapsed,
                        rx.hstack(
                            rx.avatar(
                                fallback=QueryUser.logged_in_user.nombre[0].upper(),
                                size="2",
                                variant="soft",
                                color_scheme="blue",
                            ),
                            rx.vstack(
                                rx.text(QueryUser.logged_in_user.nombre, size="2", weight="bold", color=rx.color("gray", 12), line_clamp=1),
                                rx.badge(
                                    rx.cond(QueryUser.is_admin, "ADMINISTRADOR", "USUARIO"),
                                    size="1",
                                    variant="surface",
                                    color_scheme=rx.cond(QueryUser.is_admin, "blue", "gray"),
                                ),
                                spacing="0",
                                align_items="start",
                            ),
                            spacing="3",
                            align_items="center",
                            padding="10px",
                            background=rx.color("gray", 3),
                            border_radius="lg",
                            width="100%",
                            margin_bottom="16px",
                        ),
                        rx.center(
                            rx.tooltip(
                                rx.avatar(
                                    fallback=QueryUser.logged_in_user.nombre[0].upper(),
                                    size="2",
                                    variant="soft",
                                    color_scheme="blue",
                                ),
                                content=QueryUser.logged_in_user.nombre,
                            ),
                            margin_bottom="16px",
                            width="100%",
                        ),
                    ),
                    width="100%",
                    padding_x=rx.cond(QueryUser.sidebar_collapsed, "0px", "12px"),
                ),
            ),
            # Footer / Versión / Logout
            rx.vstack(
                rx.cond(
                    ~QueryUser.sidebar_collapsed,
                    rx.vstack(
                        rx.button(
                            rx.hstack(
                                rx.icon(tag="log-out", size=16),
                                rx.text("Cerrar Sesión", size="2"),
                                align_items="center",
                                spacing="2",
                            ),
                            variant="ghost",
                            color_scheme="red",
                            width="100%",
                            on_click=QueryUser.logout,
                            margin_bottom="12px",
                        ),
                        rx.text("Versión 2.1.0", size="1", color=rx.color("gray", 8)),
                        rx.text("© Raúl Allué Sánchez", size="1", color=rx.color("gray", 7)),
                        spacing="0",
                        align_items="center",
                    ),
                    rx.vstack(
                        rx.icon(
                            tag="log-out", 
                            size=20, 
                            color=rx.color("red", 9),
                            cursor="pointer",
                            on_click=QueryUser.logout,
                            margin_bottom="12px",
                        ),
                        rx.text("v2.1", size="1", color=rx.color("gray", 8)),
                        align_items="center",
                    ),
                ),
                align_items="center",
                width="100%",
                padding_y="16px",
            ),
            height="100vh",
            padding=rx.cond(QueryUser.sidebar_collapsed, "20px 0px", "24px"),
            bg=rx.color("gray", 2),
            border_right=f"1px solid {rx.color('gray', 4)}",
            width=rx.cond(QueryUser.sidebar_collapsed, "64px", "280px"),
            # Responsive positioning:
            # - Desktop: Fixed at left 0.
            # - Mobile: Offset by -280px unless toggled open via State.
            left=[rx.cond(~QueryUser.sidebar_open, "-280px", "0px"), rx.cond(~QueryUser.sidebar_open, "-280px", "0px"), "0"],
            top="0",
            z_index="200",
        ),
        # Dark overlay to focus the sidebar drawer on mobile and allow closing on click.
        rx.cond(
            QueryUser.sidebar_open,
            rx.box(
                on_click=QueryUser.toggle_mobile_sidebar,
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                bg="rgba(0,0,0,0.5)",
                z_index="190",
                display=["block", "block", "none"],
            ),
        ),
        display="block",
    )
