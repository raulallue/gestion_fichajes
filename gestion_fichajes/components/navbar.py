import reflex as rx


def navbar():
    return rx.hstack(
        rx.link(
            rx.button("Inicio", variant="surface", size="3"),
            href="/",
            style={"text-decoration": "none"},
        ),
        rx.link(
            rx.button("Añadir Usuario", variant="surface", size="3"),
            href="/add_user",
            style={"text-decoration": "none"},
        ),
        rx.link(
            rx.button(
                "Servicios",
                size="3",
                variant="surface",
            ),
            href="/servicios",
            style={"text-decoration": "none"},
        ),
        justify="center",
        spacing="6",
        padding="15px",
        width="100%",
        bg="gray.100",
        # border_bottom="1px solid #ccc",
        box_shadow="md",
    )
