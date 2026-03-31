import reflex as rx
from gestion_fichajes.components.link_button import link_button


def header():
    return rx.hstack(
        link_button("Inicio", "/", "house"),
        link_button("Añadir Usuario", "/add_user", "user-plus"),
        link_button("Servicios", "/servicios", "database-backup"),
        justify="center",
        # spacing="6",
        padding="5px",
        width="100%",
        margin_bottom="10px",
        bg=rx.color("blue", 5),
        border_radius="0px 0px 10px 10px",
        # box_shadow="md",
    )
