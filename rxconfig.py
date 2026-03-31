import reflex as rx

config = rx.Config(
    app_name="gestion_fichajes",
    plugins=[rx.plugins.TailwindV3Plugin()],
    disable_plugins=[rx.plugins.sitemap.SitemapPlugin],
    db_url="sqlite:///reflex.db",
    frontend_port=3004,
    backend_port=8004,
    show_built_with_reflex=False,
)
