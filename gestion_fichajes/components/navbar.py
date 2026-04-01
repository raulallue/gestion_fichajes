import reflex as rx
from gestion_fichajes.state.state import QueryUser

def navbar() -> rx.Component:
    """A floating top header that appears only on mobile/tablet to provide a hamburger menu."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.image(src="/logo.png", width="28px", height="auto", border_radius="4px"),
                rx.heading("AutoFichaje", size="4", weight="bold"),
                spacing="2",
                align_items="center",
            ),
            rx.spacer(),
            rx.icon(
                tag="menu",
                size=24,
                cursor="pointer",
                on_click=QueryUser.toggle_mobile_sidebar,
                color=rx.color("gray", 11),
            ),
            width="100%",
            align_items="center",
            padding="12px 20px",
        ),
        display=["block", "block", "none"], # Show only on mobile/tablet
        position="fixed",
        top="0",
        left="0",
        width="100%",
        z_index="150",
        bg=rx.color("gray", 2),
        border_bottom=f"1px solid {rx.color('gray', 4)}",
    )
