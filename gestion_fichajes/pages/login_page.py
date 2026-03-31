import reflex as rx
from gestion_fichajes.state.state import QueryUser

def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            # Encabezado con Logo
            rx.vstack(
                rx.box(
                    rx.image(src="/logo.png", width="48px", height="auto", border_radius="8px", background="white"),
                    padding="12px",
                    background=rx.color("blue", 9),
                    border_radius="xl",
                    box_shadow=f"0 0 20px {rx.color('blue', 7)}",
                ),
                rx.heading("AutoFichaje", size="8", weight="bold", color=rx.color("gray", 12)),
                rx.text("Introduce tus credenciales de ATR", size="2", color=rx.color("gray", 10)),
                spacing="3",
                align_items="center",
                margin_bottom="24px",
            ),
            
            # Formulario
            rx.vstack(
                rx.vstack(
                    rx.text("Usuario / Email", size="2", weight="medium", color=rx.color("gray", 11)),
                    rx.input(
                        rx.input.slot(rx.icon(tag="user", size=16, color=rx.color("gray", 8))),
                        placeholder="ejemplo@dominio.com",
                        value=QueryUser.auth_usuario,
                        on_change=QueryUser.set_auth_usuario,
                        width="100%",
                        variant="soft",
                        size="3",
                        radius="large",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Contraseña", size="2", weight="medium", color=rx.color("gray", 11)),
                    rx.input(
                        rx.input.slot(rx.icon(tag="lock", size=16, color=rx.color("gray", 8))),
                        placeholder="••••••••",
                        type="password",
                        value=QueryUser.auth_contraseña,
                        on_change=QueryUser.set_auth_contraseña,
                        width="100%",
                        variant="soft",
                        size="3",
                        radius="large",
                        on_key_down=QueryUser.handle_login_keydown,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.button(
                    "Entrar en el Portal",
                    rx.icon(tag="arrow-right", size=18),
                    on_click=QueryUser.login,
                    width="100%",
                    size="3",
                    color_scheme="blue",
                    variant="solid",
                    margin_top="12px",
                    cursor="pointer",
                    _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.1)"},
                    transition="all 0.2s",
                ),
                spacing="4",
                width="100%",
            ),
            
            # Footer del login
            rx.text(
                "© 2026 Raúl Allué Sánchez",
                size="1",
                color=rx.color("gray", 8),
                margin_top="32px",
            ),
            
            spacing="0",
            padding="48px",
            background="rgba(255, 255, 255, 0.8)",
            backdrop_filter="blur(16px) saturate(180%)",
            border=f"1px solid {rx.color('gray', 5)}",
            border_radius="32px",
            box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            width="420px",
            align_items="center",
        ),
        width="100%",
        height="100vh",
        background="""
            radial-gradient(at 0% 0%, hsla(210,100%,95%,1) 0, transparent 50%),
            radial-gradient(at 50% 0%, hsla(220,100%,90%,1) 0, transparent 50%),
            radial-gradient(at 100% 0%, hsla(230,100%,95%,1) 0, transparent 50%),
            radial-gradient(at 50% 100%, hsla(240,100%,98%,1) 0, transparent 50%),
            #f8fafc
        """,
    )
