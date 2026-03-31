import reflex as rx
import datetime


def footer():
    return rx.hstack(
        rx.cond(
            datetime.datetime.today().year > 2025,
            rx.text(
                f"© 2025 - {datetime.datetime.today().year} Gestion automática de fichajes - ElRa",
                color=rx.color("indigo", 9),
                weight="medium",
            ),
            rx.text(
                "© 2025 Gestion automática de fichajes - ElRa",
                color=rx.color("indigo", 11),
                weight="medium",
            ),
        ),
        justify="center",
        # spacing="4",
        padding="5px",
        width="100%",
        margin_y="10px",
        border_radius="10px 10px 0px 0px",
        bg=rx.color("blue", 5),
    )
