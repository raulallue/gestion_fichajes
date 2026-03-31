import reflex as rx


def link_button(
    text: str, href: str, icon: str, external: bool = False
) -> rx.Component:
    return rx.link(
        rx.button(rx.icon(icon), text, variant="surface", size="2"),
        href=href,
        is_external=external,
    )
