import reflex as rx
import httpx
import os
import calendar
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List, Optional, Dict, Any
from gestion_fichajes.models.model import User, Vacation, NationalHoliday, GlobalSettings
from gestion_fichajes.services.clock_in import ATRService
import asyncio
from sqlmodel import select


# Global flag to ensure the background engine runs only once per server process.
_ENGINE_STARTED = False
_REFRESH_STARTED = False

class QueryUser(rx.State):
    @rx.event(background=True)
    async def check_engine(self):
        """Ensure the background engine is running."""
        global _ENGINE_STARTED
        if _ENGINE_STARTED:
            return
        
        async with self:
            if _ENGINE_STARTED:
                return
            _ENGINE_STARTED = True
        
        from gestion_fichajes.services.engine import daemon_loop
        asyncio.create_task(daemon_loop())

    user_edit_id: Optional[int] = None
    nuevo_nombre: str = ""
    nuevo_usuario: str = ""
    nuevo_contraseña: str = ""
    nuevo_person_id: str = ""  # Nuevo campo para ATR
    nuevo_work_days: List[int] = [0, 1, 2, 3, 4]  # Mon-Fri
    nuevo_vacaciones: bool = False
    nuevo_intensiva: bool = False
    nuevo_activo: bool = True
    nuevo_rol: str = "user"
    
    # Autenticación
    logged_in_user: Optional[User] = None
    auth_usuario: str = ""
    auth_contraseña: str = ""

    def set_auth_usuario(self, val: str):
        self.auth_usuario = val

    def set_auth_contraseña(self, val: str):
        self.auth_contraseña = val

    def set_nuevo_rol(self, val: str):
        self.nuevo_rol = val

    @rx.var
    def is_authenticated(self) -> bool:
        return self.logged_in_user is not None

    @rx.var
    def is_admin(self) -> bool:
        return self.logged_in_user is not None and self.logged_in_user.rol == "admin"

    def logout(self):
        self.logged_in_user = None
        return rx.redirect("/login")

    def handle_login_keydown(self, key: str):
        if key == "Enter":
            return self.login()

    def login(self):
        if not self.auth_usuario or not self.auth_contraseña:
            return rx.toast.error("Usuario y contraseña requeridos")
            
        with rx.session() as session:
            user = session.query(User).filter(
                User.usuario == self.auth_usuario,
                User.contraseña == self.auth_contraseña
            ).first()
            
            if user:
                self.logged_in_user = user
                self.auth_usuario = ""
                self.auth_contraseña = ""
                return rx.redirect("/")
            else:
                return rx.toast.error("Credenciales incorrectas")
    def set_nuevo_activo(self, val: bool):
        self.nuevo_activo = val
    nuevo_chin_1: str = ""
    nuevo_chout_1: str = ""
    nuevo_chin_2: str = ""
    nuevo_chout_2: str = ""
    
    # Fichaje Manual
    manual_fichaje_date: str = ""
    manual_fichaje_in: str = ""
    manual_fichaje_out: str = ""
    manual_fichaje_notes: str = "" # Nueva variable para notas
    show_manual_dialog: bool = False

    def set_manual_fichaje_date(self, val: str):
        self.manual_fichaje_date = val

    def set_manual_fichaje_in(self, val: str):
        self.manual_fichaje_in = val

    def set_manual_fichaje_out(self, val: str):
        self.manual_fichaje_out = val

    def set_manual_fichaje_notes(self, val: str):
        self.manual_fichaje_notes = val

    # Edición de Fichaje
    edit_fichaje_id: int = -1
    edit_fichaje_date: str = ""
    edit_fichaje_in: str = ""
    edit_fichaje_out: str = ""
    edit_fichaje_notes: str = "" # Nueva variable para notas
    show_edit_dialog: bool = False
    raw_history_fichajes: Dict[int, Any] = {}

    def set_edit_fichaje_date(self, val: str):
        self.edit_fichaje_date = val

    def set_edit_fichaje_in(self, val: str):
        self.edit_fichaje_in = val

    def set_edit_fichaje_out(self, val: str):
        self.edit_fichaje_out = val

    def set_edit_fichaje_notes(self, val: str):
        self.edit_fichaje_notes = val

    # Dashboard Stats
    dash_total_users: str = "0"
    dash_working_now: str = "0"
    dash_finished_today: str = "0"
    dash_potential_today: str = "0"
    dash_vacations_today: str = "0"
    dash_inactive_today: str = "0"
    dash_total_monthly_punches: str = "0"
    dash_recent_punches: List[Dict[str, str]] = []
    
    # Próximos turnos
    upcoming_window: int = 3
    dash_upcoming_shifts: List[Dict[str, str]] = []
    show_only_pending: bool = False

    def set_upcoming_window(self, val: Any):
        self.upcoming_window = int(val)
        return QueryUser.fetch_dashboard_data

    def set_show_only_pending(self, val: bool):
        self.show_only_pending = val
        return QueryUser.fetch_dashboard_data

    # UI Tab Control
    active_tab: str = "perfil"
    def set_active_tab(self, val: str):
        self.active_tab = val
        if val == "historial":
            return QueryUser.fetch_history

    search_value: str = ""
    
    # Deletion Confirmation
    show_confirm_dialog: bool = False
    delete_confirm_user_id: Optional[int] = None
    delete_confirm_user_username: str = ""
    delete_confirm_input: str = ""
    
    # Vacations Dialog (Deprecated but kept for stability)
    show_vacation_dialog: bool = False
    selected_user_name: str = ""
    
    # Visibility Toggle
    show_password: bool = False
    sidebar_collapsed: bool = False
    show_add_user_modal: bool = False

    def toggle_add_user_modal(self):
        self.show_add_user_modal = not self.show_add_user_modal
        if self.show_add_user_modal:
            self.reset_form()
    
    # History/Clock-ins
    history_fichajes: list[dict] = []
    history_range: str = "7" # Default 7 days
    history_sort_key: str = "fecha"
    history_sort_asc: bool = False

    def sort_history(self, key: str):
        if self.history_sort_key == key:
            self.history_sort_asc = not self.history_sort_asc
        else:
            self.history_sort_key = key
            self.history_sort_asc = True
        self.history_fichajes = sorted(
            self.history_fichajes,
            key=lambda h: h.get(key, ""),
            reverse=not self.history_sort_asc,
        )

    # Calendar Navigation
    current_month: int = date.today().month
    current_year: int = date.today().year
    
    users: list[User] = []
    user_id: Optional[int] = None

    # Campos para gestión de vacaciones
    selected_user_id: Optional[int] = None
    nueva_fecha_vacacion: str = ""
    nueva_fecha_fin: str = ""  # Nuevo campo para rango
    vacaciones_usuario: List[Vacation] = []

    def cargar_usuarios(self):
        """Load users from the database."""
        try:
            with rx.session() as session:
                db_users = session.query(User).all()
                self.users = db_users
                if not db_users:
                    return rx.toast.info("No hay usuarios registrados.")
        except Exception as e:
            rx.window_alert(f"Error loading users: {e}")
            self.users = []
            
    @rx.var
    def filtered_users_with_status(self) -> list[tuple[User, bool, str]]:
        if not self.logged_in_user:
            return []
            
        today = date.today()
        with rx.session() as session:
            vacation_user_ids = {
                v.user_id for v in session.query(Vacation).filter(Vacation.date == today).all()
            }
            
        days_map = {"0": "L", "1": "M", "2": "X", "3": "J", "4": "V", "5": "S", "6": "D"}

        # RBAC: Si no es admin, solo se ve a sí mismo
        if self.logged_in_user.rol == "admin":
            users_to_filter = self.users
        else:
            users_to_filter = [u for u in self.users if u.id == self.logged_in_user.id]

        if self.search_value:
            sv = self.search_value.lower()
            users_to_filter = [
                u for u in users_to_filter 
                if sv in u.nombre.lower() or sv in u.usuario.lower()
            ]
            
        return [
            (u, u.id in vacation_user_ids, ",".join([days_map.get(d.strip(), d.strip()) for d in u.work_days.split(",") if d.strip()]))
            for u in users_to_filter
        ]

    @rx.var
    def filtered_users(self) -> List[User]:
        if not self.logged_in_user:
            return []
            
        # RBAC: Si no es admin, solo se ve a sí mismo
        if self.logged_in_user.rol == "admin":
            users_to_filter = self.users
        else:
            users_to_filter = [u for u in self.users if u.id == self.logged_in_user.id]

        if not self.search_value:
            return users_to_filter
            
        return [
            u for u in users_to_filter 
            if self.search_value.lower() in u.nombre.lower() or 
               self.search_value.lower() in u.usuario.lower()
        ]

    def check_auth(self):
        """Redirigir al login si no está autenticado."""
        if not self.is_authenticated:
            return rx.redirect("/login")

    @rx.var
    def nombre_usuarios(self) -> List[str]:
        return [user.nombre for user in self.users]

    def set_search_value(self, value: str):
        self.search_value = value

    def set_delete_confirm_input(self, value: str):
        self.delete_confirm_input = value

    def open_delete_dialog(self, user_id: int, username: str):
        self.delete_confirm_user_id = user_id
        self.delete_confirm_user_username = username
        self.delete_confirm_input = ""
        self.show_confirm_dialog = True

    def close_delete_dialog(self):
        self.show_confirm_dialog = False
        self.delete_confirm_user_id = None
        self.delete_confirm_input = ""

    def open_vacation_manager(self, user_id: int, user_name: str):
        self.selected_user_id = user_id
        self.selected_user_name = user_name
        self.cargar_vacaciones()
        self.show_vacation_dialog = True

    def close_vacation_manager(self):
        self.show_vacation_dialog = False
        self.selected_user_id = None
        self.selected_user_name = ""

    # Explicit Setters
    def set_nuevo_nombre(self, value: str):
        self.nuevo_nombre = value

    def set_nuevo_usuario(self, value: str):
        self.nuevo_usuario = value

    def set_nuevo_contraseña(self, value: str):
        self.nuevo_contraseña = value

    def set_nuevo_person_id(self, value: str):
        self.nuevo_person_id = value

    def set_nuevo_vacaciones(self, value: bool):
        self.nuevo_vacaciones = value

    def set_nuevo_intensiva(self, value: bool):
        self.nuevo_intensiva = value

    def set_nueva_fecha_vacacion(self, value: str):
        self.nueva_fecha_vacacion = value
        # Actualizar siempre la fecha de fin al cambiar el inicio para facilitar selección de día único
        self.nueva_fecha_fin = value

    def set_nueva_fecha_fin(self, value: str):
        self.nueva_fecha_fin = value

    def set_nuevo_chin_1(self, value: str):
        self.nuevo_chin_1 = value

    def set_nuevo_chout_1(self, value: str):
        self.nuevo_chout_1 = value

    def set_nuevo_chin_2(self, value: str):
        self.nuevo_chin_2 = value

    def set_nuevo_chout_2(self, value: str):
        self.nuevo_chout_2 = value

    def toggle_vacaciones(self, user_id: int):
        """Toggle the quick vacation status of a user."""
        try:
            with rx.session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.vacaciones = not user.vacaciones
                    session.add(user)
                    session.commit()
                    self.cargar_usuarios()
                else:
                    rx.window_alert(f"User with ID {user_id} not found.")
        except Exception as e:
            print(f"Error toggling vacaciones for user {user_id}: {e}")

    def toggle_jornada(self, user_id: int):
        """Toggle the jornada status of a user."""
        try:
            with rx.session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.intensiva = not user.intensiva
                    session.add(user)
                    session.commit()
                    self.cargar_usuarios()
                else:
                    rx.window_alert(f"User with ID {user_id} not found.")
        except Exception as e:
            print(f"Error toggling jornada for user {user_id}: {e}")

    def validate_user(self):
        # Validaciones
        if not self.nuevo_nombre.strip():
            return "El nombre es obligatorio."
        if not self.nuevo_usuario.strip():
            return "El usuario es obligatorio."
        if not self.nuevo_contraseña.strip():
            return "La contraseña es obligatoria."
        if not self.nuevo_chin_1.strip():
            return "El horario de inicio de jornada 1 es obligatorio."
        if not self.nuevo_chout_1.strip():
            return "El horario de salida de jornada 1 es obligatorio."

        try:
            chin1 = datetime.strptime(self.nuevo_chin_1, "%H:%M").time()
            chout1 = datetime.strptime(self.nuevo_chout_1, "%H:%M").time()
            if chout1 <= chin1:
                return "La hora de salida de jornada 1 no puede ser anterior o igual a la de entrada."
        except ValueError:
            return "Formato de hora inválido para jornada 1."

        if not self.nuevo_intensiva:
            if not self.nuevo_chin_2.strip() or not self.nuevo_chout_2.strip():
                return "El horario de jornada 2 es obligatorio para jornada no intensiva."
            try:
                chin2 = datetime.strptime(self.nuevo_chin_2, "%H:%M").time()
                chout2 = datetime.strptime(self.nuevo_chout_2, "%H:%M").time()
                if chout2 <= chin2:
                    return "La hora de salida de jornada 2 no puede ser anterior o igual a la de entrada."
                if chin2 <= chout1:
                    return "La jornada 2 debe empezar después de la jornada 1."
            except ValueError:
                return "Formato de hora inválido para jornada 2."
        
        # Validaciones adicionales de lógica de negocio (ej: no permitir salidas menores que entradas)
        # Esto ya está cubierto arriba, pero nos aseguramos de que sea estricto.

        return True

    async def add_user(self):
        val = self.validate_user()
        if val is not True:
            return rx.toast.error(val)

        try:
            # Automatar extracción de Person ID
            atr = ATRService(self.nuevo_usuario, self.nuevo_contraseña)
            login_res = await atr.login()
            if not login_res.get("success"):
                return rx.toast.error(f"Error de login en ATR: {login_res.get('error')}")
            
            person_id = str(login_res.get("person_id"))
            if not person_id:
                return rx.toast.error("No se pudo extraer el ID de Persona de ATR.")

            with rx.session() as session:
                user_exists = session.query(User).filter(User.usuario == self.nuevo_usuario).first()
                if user_exists:
                    return rx.toast.error("El usuario ya existe.")

                new_user = User(
                    nombre=self.nuevo_nombre,
                    usuario=self.nuevo_usuario,
                    contraseña=self.nuevo_contraseña,
                    person_id=person_id,
                    work_days=",".join(map(str, self.nuevo_work_days)),
                    vacaciones=self.nuevo_vacaciones,
                    intensiva=self.nuevo_intensiva,
                    activo=self.nuevo_activo,
                    chin_1=datetime.strptime(self.nuevo_chin_1, "%H:%M").time(),
                    chout_1=datetime.strptime(self.nuevo_chout_1, "%H:%M").time(),
                    chin_2=datetime.strptime(self.nuevo_chin_2, "%H:%M").time() if self.nuevo_chin_2 else None,
                    chout_2=datetime.strptime(self.nuevo_chout_2, "%H:%M").time() if self.nuevo_chout_2 else None,
                    rol=self.nuevo_rol,
                )
                session.add(new_user)
                session.commit()
                self.reset_form()
                self.cargar_usuarios()
                return [rx.toast.success("Usuario añadido correctamente!"), rx.redirect("/usuarios")]
        except Exception as e:
            return rx.window_alert(f"Error añadiendo el usuario: {e}")

    def delete_user(self):
        if self.delete_confirm_input != self.delete_confirm_user_username:
            return rx.toast.error("El nombre de usuario no coincide. No se puede eliminar.")

        try:
            with rx.session() as session:
                user = session.query(User).filter(User.id == self.delete_confirm_user_id).first()
                if user:
                    session.delete(user)
                    session.commit()
                    self.cargar_usuarios()
                    self.close_delete_dialog()
                    return rx.toast.success("Usuario eliminado correctamente!")
        except Exception as e:
            return rx.window_alert(f"Error eliminando el usuario: {e}")

    @rx.event
    def cargar_usuario_para_editar(self, user_id: int):
        with rx.session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                self.user_edit_id = user.id
                self.nuevo_nombre = user.nombre
                self.nuevo_usuario = user.usuario
                self.nuevo_contraseña = user.contraseña
                self.nuevo_person_id = user.person_id
                self.nuevo_work_days = [int(d) for d in user.work_days.split(",") if d]
                self.nuevo_vacaciones = user.vacaciones
                self.nuevo_intensiva = user.intensiva
                self.nuevo_activo = user.activo
                self.nuevo_chin_1 = user.chin_1.strftime("%H:%M")
                self.nuevo_chout_1 = user.chout_1.strftime("%H:%M")
                self.nuevo_chin_2 = user.chin_2.strftime("%H:%M") if user.chin_2 else ""
                self.nuevo_chout_2 = user.chout_2.strftime("%H:%M") if user.chout_2 else ""
                self.nuevo_rol = user.rol
                
                # Cargar vacaciones para este usuario
                self.selected_user_id = user.id
                self.cargar_vacaciones()
                self.set_current_to_today()
                
                # Reset history and tab when loading a new user
                self.history_fichajes = []
                self.active_tab = "perfil"
                
                return rx.redirect("/usuario")

    def cargar_usuario_historial(self, user_id: int):
        """Load a user and navigate directly to the historial tab."""
        with rx.session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                self.user_edit_id = user.id
                self.nuevo_nombre = user.nombre
                self.nuevo_usuario = user.usuario
                self.nuevo_contraseña = user.contraseña
                self.nuevo_person_id = user.person_id
                self.nuevo_work_days = [int(d) for d in user.work_days.split(",") if d]
                self.nuevo_vacaciones = user.vacaciones
                self.nuevo_intensiva = user.intensiva
                self.nuevo_activo = user.activo
                self.nuevo_chin_1 = user.chin_1.strftime("%H:%M")
                self.nuevo_chout_1 = user.chout_1.strftime("%H:%M")
                self.nuevo_chin_2 = user.chin_2.strftime("%H:%M") if user.chin_2 else ""
                self.nuevo_chout_2 = user.chout_2.strftime("%H:%M") if user.chout_2 else ""
                self.nuevo_rol = user.rol
                self.selected_user_id = user.id
                self.history_fichajes = []
                self.active_tab = "historial"
                return rx.redirect("/usuario")

    def check_user_details_access(self):
        """Redirigir si se intenta entrar a detalles sin un usuario cargado o sin permiso."""
        if not self.logged_in_user:
            return rx.redirect("/login")
            
        if not self.user_edit_id:
            # Si no hay ID de edición, intentamos cargar el del propio usuario como fallback
            return self.cargar_usuario_para_editar(self.logged_in_user.id)
            
        # RBAC: Si no es admin y el ID no coincide, fuera.
        if self.logged_in_user.rol != "admin" and self.user_edit_id != self.logged_in_user.id:
            return rx.redirect("/")

    def check_vacations_access(self):
        """Redirigir si un no-admin intenta acceder a vacaciones."""
        if not self.logged_in_user:
            return rx.redirect("/login")
        if self.logged_in_user.rol != "admin":
            return rx.redirect("/")

    @rx.event
    def update_user(self):
        val = self.validate_user()
        if val is not True:
            return rx.toast.error(val)

        try:
            with rx.session() as session:
                user = session.query(User).filter(User.id == self.user_edit_id).first()
                if not user:
                    return rx.window_alert("Usuario no encontrado.")

                user.nombre = self.nuevo_nombre
                user.usuario = self.nuevo_usuario
                user.contraseña = self.nuevo_contraseña
                user.person_id = self.nuevo_person_id
                user.work_days = ",".join(map(str, self.nuevo_work_days))
                user.vacaciones = self.nuevo_vacaciones
                user.intensiva = self.nuevo_intensiva
                user.activo = self.nuevo_activo
                
                # Solo admin puede cambiar el rol
                if self.is_admin:
                    user.rol = self.nuevo_rol
                    
                user.chin_1 = datetime.strptime(self.nuevo_chin_1, "%H:%M").time()
                user.chout_1 = datetime.strptime(self.nuevo_chout_1, "%H:%M").time()
                user.chin_2 = datetime.strptime(self.nuevo_chin_2, "%H:%M").time() if self.nuevo_chin_2 else None
                user.chout_2 = datetime.strptime(self.nuevo_chout_2, "%H:%M").time() if self.nuevo_chout_2 else None

                session.commit()
                # Si se edita a sí mismo, actualizar el objeto en sesión
                if user.id == self.logged_in_user.id:
                    self.logged_in_user = user
                    
                self.reset_form()
                
                if self.is_admin:
                    return rx.redirect("/usuarios")
                else:
                    return rx.toast.success("Perfil actualizado correctamente")
                self.cargar_usuarios()
                return [rx.toast.success("Usuario actualizado correctamente."), rx.redirect("/usuarios")]
        except Exception as e:
            return rx.window_alert(f"Error actualizando el usuario: {e}")

    def reset_form(self):
        self.nuevo_nombre = ""
        self.nuevo_usuario = ""
        self.nuevo_contraseña = ""
        self.nuevo_person_id = ""
        self.nuevo_work_days = [0, 1, 2, 3, 4]
        self.nuevo_vacaciones = False
        self.nuevo_intensiva = True
        self.nuevo_activo = True
        self.nuevo_chin_1 = ""
        self.nuevo_chout_1 = ""
        self.nuevo_chin_2 = ""
        self.nuevo_chout_2 = ""
        self.user_edit_id = None
        self.selected_user_id = None
        self.vacaciones_usuario = []
        self.show_password = False

    def toggle_show_password(self):
        self.show_password = not self.show_password

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

    @rx.event(background=True)
    async def fetch_history(self):
        """Fetch clock-in history for the current edit user."""
        if not self.user_edit_id:
            return

        async with self:
            # Encontrar el usuario en la lista o BD para sus credenciales y person_id
            with rx.session() as session:
                user = session.query(User).filter(User.id == self.user_edit_id).first()
                if not user:
                    return

            # Calcular fechas
            until_dt = datetime.now()
            days = int(self.history_range)
            from_dt = until_dt - timedelta(days=days)
            
            since_str = from_dt.strftime("%Y-%m-%dT00:00:00")
            until_str = until_dt.strftime("%Y-%m-%dT23:59:59")
            
            # Consultar API
            # Usamos el usuario y contraseña del propio usuario para consultar sus fichajes
            # El usuario de info.txt es admin y sirve para todos, pero aquí usamos las del usuario
            service = ATRService(user.usuario, user.contraseña)
            res = await service.get_clock_ins(user.person_id, since_str, until_str)
            
            if res.get("success"):
                data_dict = res.get("data", {})
                data = data_dict.get("rows", []) if isinstance(data_dict, dict) else (data_dict if isinstance(data_dict, list) else [])
                # Formatear datos para la tabla
                formatted = []
                self.raw_history_fichajes.clear()
                for entry in data:
                    init = entry.get("init_date", "")
                    end = entry.get("end_date", "")
                    item_id = entry.get("id")
                    if item_id:
                        self.raw_history_fichajes[item_id] = entry
                    # Formatear fechas ISO a algo legible DD-MM-YYYY HH:mm
                    try:
                        local_tz = ZoneInfo("Europe/Madrid")
                        dt_init = datetime.fromisoformat(init.replace("Z", "+00:00")).astimezone(local_tz)
                        dt_end = datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(local_tz) if end else None
                        formatted.append({
                            "id": item_id or -1,
                            "fecha": dt_init.strftime("%d-%m-%Y"),
                            "fecha_sort": init, # Usar ISO string para ordenar
                            "entrada": dt_init.strftime("%H:%M"),
                            "salida": dt_end.strftime("%H:%M") if dt_end else "---",
                            "notas": entry.get("notes", "")
                        })
                    except:
                        formatted.append({
                            "id": item_id or -1,
                            "fecha": init[:10],
                            "fecha_sort": init,
                            "entrada": init[11:16],
                            "salida": end[11:16] if end else "---",
                            "notas": entry.get("notes", "")
                        })
                
                # Ordenar por fecha descendente (más recientes primero)
                self.history_fichajes = sorted(formatted, key=lambda x: x["fecha_sort"], reverse=True)
            else:
                return rx.toast.error(f"Error cargando historial: {res.get('error')}")

    def change_history_range(self, val: str):
        self.history_range = val
        return QueryUser.fetch_history

    def handle_tab_change(self, val: str):
        self.active_tab = val
        if val == "historial":
            return QueryUser.fetch_history

    # Gestión de Fichaje Manual
    def toggle_manual_dialog(self):
        self.show_manual_dialog = not self.show_manual_dialog
        if not self.show_manual_dialog:
            self.manual_fichaje_date = ""
            self.manual_fichaje_in = ""
            self.manual_fichaje_out = ""
            self.manual_fichaje_notes = ""

    async def add_manual_fichaje(self):
        if not self.manual_fichaje_date or not self.manual_fichaje_in or not self.manual_fichaje_out:
            yield rx.toast.error("Por favor completa la fecha y las horas de entrada y salida.")
            return
        
        with rx.session() as session:
            user = session.query(User).filter(User.id == self.user_edit_id).first()
            if not user or not user.person_id:
                yield rx.toast.error("Usuario no válido para fichar.")
                return
        
        try:
            # Combinar y asignar zona horaria (Local -> UTC)
            local_tz = ZoneInfo("Europe/Madrid")
            date_obj = datetime.strptime(self.manual_fichaje_date, "%Y-%m-%d").date()
            time_in_obj = datetime.strptime(self.manual_fichaje_in, "%H:%M").time()
            time_out_obj = datetime.strptime(self.manual_fichaje_out, "%H:%M").time()
            
            init_dt = datetime.combine(date_obj, time_in_obj, tzinfo=local_tz)
            end_dt = datetime.combine(date_obj, time_out_obj, tzinfo=local_tz)
            
            service = ATRService(user.usuario, user.contraseña)
            success = await service.create_fichaje(
                user.person_id, init_dt, end_dt, self.manual_fichaje_notes
            )
            
            if success:
                self.toggle_manual_dialog()
                yield rx.toast.success("Fichaje manual añadido correctamente.")
                yield QueryUser.fetch_history
            else:
                yield rx.toast.error("Error al enviar fichaje manual a ATR.")
        except Exception as e:
            yield rx.toast.error(f"Error procesando fecha u hora: {e}")

    def toggle_edit_dialog(self):
        self.show_edit_dialog = not self.show_edit_dialog
        if not self.show_edit_dialog:
            self.edit_fichaje_notes = ""

    def open_edit_dialog(self, item_id: int):
        self.edit_fichaje_id = item_id
        raw_row = self.raw_history_fichajes.get(item_id)
        if not raw_row:
            return rx.toast.error("No se encontraron los datos del fichaje selecciondo.")
        
        try:
            local_tz = ZoneInfo("Europe/Madrid")
            init = raw_row.get("init_date", "")
            end = raw_row.get("end_date", "")
            dt_init = datetime.fromisoformat(init.replace("Z", "+00:00")).astimezone(local_tz)
            
            self.edit_fichaje_date = dt_init.strftime("%Y-%m-%d")
            self.edit_fichaje_in = dt_init.strftime("%H:%M")
            if end:
                dt_end = datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(local_tz)
                self.edit_fichaje_out = dt_end.strftime("%H:%M")
            else:
                self.edit_fichaje_out = ""
                
            self.edit_fichaje_notes = raw_row.get("notes", "") or ""
            self.show_edit_dialog = True
        except Exception as e:
            return rx.toast.error(f"Error parseando el fichaje {item_id}: {e}")

    async def update_manual_fichaje(self):
        if not self.edit_fichaje_date or not self.edit_fichaje_in:
            yield rx.toast.error("La fecha y la hora de entrada son obligatorias.")
            return
            
        if self.edit_fichaje_id == -1 or self.edit_fichaje_id not in self.raw_history_fichajes:
            yield rx.toast.error("No se puede editar este registro.")
            return
            
        with rx.session() as session:
            user = session.query(User).filter(User.id == self.user_edit_id).first()
            if not user or not user.person_id:
                yield rx.toast.error("Usuario no válido para operar en ATR.")
                return

        try:
            local_tz = ZoneInfo("Europe/Madrid")
            date_obj = datetime.strptime(self.edit_fichaje_date, "%Y-%m-%d").date()
            time_in_obj = datetime.strptime(self.edit_fichaje_in, "%H:%M").time()
            init_dt = datetime.combine(date_obj, time_in_obj, tzinfo=local_tz).astimezone(timezone.utc)
            
            end_dt = None
            if self.edit_fichaje_out:
                time_out_obj = datetime.strptime(self.edit_fichaje_out, "%H:%M").time()
                end_dt = datetime.combine(date_obj, time_out_obj, tzinfo=local_tz).astimezone(timezone.utc)
            
            raw_row = self.raw_history_fichajes[self.edit_fichaje_id]
            update_payload = dict(raw_row)
            update_payload["notes"] = self.edit_fichaje_notes 
            update_payload["init_date"] = init_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if end_dt:
                update_payload["end_date"] = end_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                update_payload["end_date"] = None
                
            service = ATRService(user.usuario, user.contraseña)
            success = await service.update_fichaje(self.edit_fichaje_id, update_payload)
            
            if success:
                self.toggle_edit_dialog()
                yield rx.toast.success("Fichaje actualizado a la perfección.")
                yield QueryUser.fetch_history
            else:
                yield rx.toast.error(f"Error al actualizar el registro en ATR.")
                
        except Exception as e:
            yield rx.toast.error(f"Error formateando la actualización: {e}")

    async def reset_auto_flags(self):
        """Resetea las banderas de automatización para el usuario actual (Debug)."""
        if not self.user_edit_id:
            return
            
        with rx.session() as session:
            user = session.query(User).filter(User.id == self.user_edit_id).first()
            if user:
                user.last_auto_in_1 = None
                user.last_auto_out_1 = None
                user.last_auto_in_2 = None
                user.last_auto_out_2 = None
                session.add(user)
                session.commit()
                yield rx.toast.success("Banderas de automatización corregidas. Ya puedes volver a fichar automáticamente hoy.")
                yield QueryUser.fetch_dashboard_data
            else:
                yield rx.toast.error("No se pudo resetear el usuario.")

    # Gestión de Vacaciones
    def seleccionar_usuario_por_nombre(self, nombre: str):
        for user in self.users:
            if user.nombre == nombre:
                self.selected_user_id = user.id
                self.cargar_vacaciones()
                return

    def toggle_work_day(self, day: int):
        if day in self.nuevo_work_days:
            self.nuevo_work_days.remove(day)
        else:
            self.nuevo_work_days.append(day)
        self.nuevo_work_days = sorted(self.nuevo_work_days)

    def set_selected_user(self, user_id: int):
        self.selected_user_id = user_id
        self.cargar_vacaciones()

    def cargar_vacaciones(self):
        if not self.selected_user_id:
            return
        with rx.session() as session:
            self.vacaciones_usuario = session.query(Vacation).filter(Vacation.user_id == self.selected_user_id).all()

    def add_vacation_day(self):
        if not self.selected_user_id or not self.nueva_fecha_vacacion:
            return rx.toast.error("Seleccione al menos un usuario y una fecha de inicio.")
        
        try:
            inicio = datetime.strptime(self.nueva_fecha_vacacion, "%Y-%m-%d").date()
            if self.nueva_fecha_fin:
                fin = datetime.strptime(self.nueva_fecha_fin, "%Y-%m-%d").date()
                if fin < inicio:
                    return rx.toast.error("La fecha de fin no puede ser anterior a la de inicio.")
            else:
                fin = inicio

            dias_añadidos = 0
            dias_duplicados = 0
            
            from datetime import timedelta
            current = inicio
            with rx.session() as session:
                while current <= fin:
                    # Evitar duplicados
                    existing = session.query(Vacation).filter(
                        Vacation.user_id == self.selected_user_id,
                        Vacation.date == current
                    ).first()
                    
                    if not existing:
                        new_vac = Vacation(date=current, user_id=self.selected_user_id)
                        session.add(new_vac)
                        dias_añadidos += 1
                    else:
                        dias_duplicados += 1
                    
                    current += timedelta(days=1)
                
                session.commit()
            
            self.cargar_vacaciones()
            self.nueva_fecha_vacacion = ""
            self.nueva_fecha_fin = ""
            
            if dias_añadidos > 0:
                ret_msg = f"Se han añadido {dias_añadidos} días de vacaciones."
                if dias_duplicados > 0:
                    ret_msg += f" ({dias_duplicados} ya existían)."
                return rx.toast.success(ret_msg)
            else:
                return rx.toast.info("No se añadieron días nuevos (ya estaban registrados).")
                
        except Exception as e:
            return rx.toast.error(f"Error: {e}")

    def delete_vacation_day(self, vac_id: int):
        with rx.session() as session:
            vac = session.query(Vacation).filter(Vacation.id == vac_id).first()
            if vac:
                session.delete(vac)
                session.commit()
                self.cargar_vacaciones()
                return rx.toast.success("Día eliminado.")

    @rx.var
    def formatted_vacaciones(self) -> list[dict]:
        # Ordenar por fecha cronológica inversa (más reciente primero)
        sorted_vac = sorted(self.vacaciones_usuario, key=lambda v: v.date, reverse=True)
        return [
            {"id": v.id, "date": v.date.strftime("%d-%m-%Y")}
            for v in sorted_vac
        ]

    @rx.var
    def total_vacation_days(self) -> int:
        return len(self.vacaciones_usuario)

    @rx.var
    def weekend_vacation_days(self) -> int:
        # Contar cuántos días caen en Sábado (5) o Domingo (6)
        return len([v for v in self.vacaciones_usuario if v.date.weekday() >= 5])

    @rx.var
    def calendar_header(self) -> str:
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{meses[self.current_month - 1]} {self.current_year}"

    @rx.var
    def calendar_days(self) -> list[dict]:
        cal = calendar.Calendar(firstweekday=0)
        try:
            # monthdatescalendar returns full weeks of date objects
            month_weeks = cal.monthdatescalendar(self.current_year, self.current_month)
        except Exception:
            return []
        
        vacation_dates = {v.date for v in self.vacaciones_usuario}
        
        # Festivos nacionales
        with rx.session() as session:
            national_holidays_rows = session.query(NationalHoliday).all()
            holidays_map = {h.date: h.name for h in national_holidays_rows}
            
        today = date.today()
        
        days_list = []
        for week in month_weeks:
            for day_date in week:
                days_list.append({
                    "day": str(day_date.day),
                    "is_vacation": day_date in vacation_dates,
                    "is_national_holiday": day_date in holidays_map,
                    "holiday_name": holidays_map.get(day_date, ""),
                    "is_today": day_date == today,
                    "is_current_month": day_date.month == self.current_month,
                    "is_empty": False
                })
        return days_list

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
            
    def set_current_to_today(self):
        self.current_month = date.today().month
        self.current_year = date.today().year

    async def _fetch_dashboard_data(self):
        """Internal logic for fetching dashboard data. Should be called inside 'async with self'."""
        if not self.logged_in_user:
            return
        with rx.session() as session:
            users = session.query(User).all()
            self.dash_total_users = str(len(users))
            
            today = date.today()
            weekday = today.weekday()
            local_tz = ZoneInfo("Europe/Madrid")
            now = datetime.now(local_tz)
            
            working = 0
            vacations = 0
            inactive = 0
            user_map = {}
            
            for u in users:
                if not u.activo:
                    inactive += 1
                    continue

                if u.person_id:
                    user_map[str(u.person_id)] = u.nombre
                
                if u.vacaciones:
                    vacations += 1
                    continue
                    
                vac = session.query(Vacation).filter(
                    Vacation.user_id == u.id,
                    Vacation.date == today.strftime("%Y-%m-%d")
                ).first()
                
                if vac:
                    vacations += 1
                else:
                    wd = [int(w) for w in u.work_days.split(",")] if u.work_days else []
                    if weekday in wd:
                        working += 1
                        
            self.dash_potential_today = str(working)
            self.dash_vacations_today = str(vacations)
            self.dash_inactive_today = str(inactive)
            
            # Granular real-time stats
            now_count = 0
            fin_count = 0
            all_recent = []
            monthly_total = 0
            
            users_to_process = [u for u in users if u.person_id]
            self.dash_total_users = str(len(users))

            fetch_user = next((u for u in users if u.activo and u.rol == "admin" and u.usuario and u.contraseña), None)
            if not fetch_user:
                fetch_user = next((u for u in users if u.activo and u.usuario and u.contraseña), None)
            
            if fetch_user:
                service = ATRService(fetch_user.usuario, fetch_user.contraseña)
                first_of_month = today.replace(day=1).strftime("%Y-%m-%d")
                until_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                
                for u in users_to_process:
                    res = await service.get_clock_ins(u.person_id, first_of_month, until_str)
                    if res.get("success"):
                        rows = res.get("data", {}).get("rows", [])
                        monthly_total += len(rows)
                        
                        today_punches = [r for r in rows if r.get("init_date", "")[:10] == today.strftime("%Y-%m-%d")]
                        
                        if today_punches:
                            today_punches.sort(key=lambda x: x.get("init_date", ""), reverse=True)
                            last_p = today_punches[0]
                            
                            if not last_p.get("end_date"):
                                now_count += 1
                            else:
                                fin_count += 1
                            
                            all_recent.append((last_p.get("init_date"), last_p, u.nombre))
            
            self.dash_working_now = str(now_count)
            self.dash_finished_today = str(fin_count)
            self.dash_total_monthly_punches = str(monthly_total)

            all_recent.sort(key=lambda x: x[0], reverse=True)
            recent_formatted = []
            for _, r, nombre in all_recent[:10]:
                init = r.get("init_date", "")
                end = r.get("end_date", "")
                try:
                    dt_init = datetime.fromisoformat(init.replace("Z", "+00:00")).astimezone(local_tz)
                    dt_end = datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(local_tz) if end else None
                    recent_formatted.append({
                        "nombre": nombre,
                        "fecha": dt_init.strftime("%d-%m-%Y"),
                        "entrada": dt_init.strftime("%H:%M"),
                        "salida": dt_end.strftime("%H:%M") if dt_end else "---"
                    })
                except:
                    recent_formatted.append({
                        "nombre": nombre,
                        "fecha": init[:10],
                        "entrada": init[11:16],
                        "salida": end[11:16] if end else "---"
                    })
            self.dash_recent_punches = recent_formatted

            # --- Upcoming Shifts Logic ---
            upcoming = []
            look_ahead_limit = now + timedelta(hours=self.upcoming_window)
            
            for u in users:
                if not u.activo or u.vacaciones:
                    continue
                    
                u_wd = [int(w) for w in u.work_days.split(",")] if u.work_days else []
                if weekday not in u_wd:
                    continue
                
                vac = session.query(Vacation).filter(
                    Vacation.user_id == u.id,
                    Vacation.date == today.strftime("%Y-%m-%d")
                ).first()
                if vac:
                    continue
                
                def get_target_dt(t: Optional[Any], offset: int):
                    if not t: return None
                    dt = datetime.combine(today, t, tzinfo=local_tz)
                    target = dt + timedelta(minutes=offset)
                    return target.replace(second=0, microsecond=0)

                off_in1 = u.today_offset_in_1 if u.last_offset_date == today else 0
                off_out1 = u.today_offset_out_1 if u.last_offset_date == today else 0
                off_in2 = u.today_offset_in_2 if u.last_offset_date == today else 0
                off_out2 = u.today_offset_out_2 if u.last_offset_date == today else 0

                targets = [
                    (get_target_dt(u.chin_1, off_in1), "Entrada 1", u.last_auto_in_1),
                    (get_target_dt(u.chout_1, off_out1), "Salida 1", u.last_auto_out_1),
                    (get_target_dt(u.chin_2, off_in2), "Entrada 2", u.last_auto_in_2),
                    (get_target_dt(u.chout_2, off_out2), "Salida 2", u.last_auto_out_2),
                ]

                for target_dt, label, last_date in targets:
                    if target_dt:
                        is_completed = last_date == today
                        if self.show_only_pending and is_completed:
                            continue

                        if now <= target_dt <= look_ahead_limit or (target_dt < now and is_completed):
                            upcoming.append({
                                "nombre": u.nombre,
                                "tipo": label,
                                "hora": target_dt.strftime("%H:%M"),
                                "estado": "Completado" if is_completed else "Pendiente",
                                "sort": target_dt.isoformat()
                            })
            
            upcoming.sort(key=lambda x: x["sort"])
            self.dash_upcoming_shifts = upcoming[:15]

    @rx.event(background=True)
    async def fetch_dashboard_data(self):
        """Fetch dashboard data manually."""
        async with self:
            await self._fetch_dashboard_data()

    @rx.event(background=True)
    async def periodic_refresh(self):
        """Periodically refresh the dashboard data."""
        global _REFRESH_STARTED
        if _REFRESH_STARTED:
            return
        
        async with self:
            if _REFRESH_STARTED:
                return
            _REFRESH_STARTED = True

        while True:
            try:
                await asyncio.sleep(300)
                async with self:
                    await self._fetch_dashboard_data()
            except Exception as e:
                print(f"Error in periodic refresh: {e}")
                await asyncio.sleep(60)

    @rx.event(background=True)
    async def run_automatic_clock_in(self):
        """Manual trigger for the automatic clock-in process (used for testing)."""
        from gestion_fichajes.services.engine import run_engine_iteration
        print("Ejecutando iteración forzada del motor de fichajes...")
        async with self:
            try:
                await run_engine_iteration()
                return rx.toast.success("Motor de fichajes ejecutado manualmente.")
            except Exception as e:
                print(f"Error en ejecución manual: {e}")
                return rx.toast.error(f"Error al ejecutar el motor: {e}")


class SettingsState(rx.State):
    national_holidays: List[NationalHoliday] = []
    new_holiday_date: str = ""
    new_holiday_name: str = ""
    margin_minutes: int = 5

    def load_settings(self):
        with rx.session() as session:
            # Cargar festivos
            self.national_holidays = session.exec(select(NationalHoliday).order_by(NationalHoliday.date)).all()
            
            # Cargar configuración global
            settings = session.exec(select(GlobalSettings)).first()
            if not settings:
                settings = GlobalSettings(margin_minutes=5)
                session.add(settings)
                session.commit()
                session.refresh(settings)
            self.margin_minutes = settings.margin_minutes

    def set_margin_minutes(self, val: Any):
        # Reflex sliders return a list of floats
        if val:
            self.margin_minutes = int(val[0])
            with rx.session() as session:
                settings = session.exec(select(GlobalSettings)).first()
                if settings:
                    settings.margin_minutes = self.margin_minutes
                    session.add(settings)
                    session.commit()

    def load_holidays(self):
        # Redundant, kept for compatibility if needed elsewhere
        return self.load_settings()

    def set_new_holiday_date(self, date_str: str):
        self.new_holiday_date = date_str

    def set_new_holiday_name(self, name: str):
        self.new_holiday_name = name

    def add_holiday(self):
        if not self.new_holiday_date or not self.new_holiday_name:
            return rx.toast.error("Fecha y nombre son obligatorios.")
        try:
            d = datetime.strptime(self.new_holiday_date, "%Y-%m-%d").date()
            with rx.session() as session:
                exists = session.query(NationalHoliday).filter(NationalHoliday.date == d).first()
                if exists:
                    return rx.toast.error("Ya existe un festivo en esta fecha.")
                hc = NationalHoliday(date=d, name=self.new_holiday_name)
                session.add(hc)
                session.commit()
            self.new_holiday_date = ""
            self.new_holiday_name = ""
            self.load_holidays()
            return rx.toast.success("Festivo añadido correctamente.")
        except Exception as e:
            return rx.toast.error(f"Error al añadir festivo: {e}")

    def delete_holiday(self, holiday_id: int):
        with rx.session() as session:
            h = session.query(NationalHoliday).filter(NationalHoliday.id == holiday_id).first()
            if h:
                session.delete(h)
                session.commit()
                self.load_holidays()
                return rx.toast.success("Festivo eliminado.")

    @rx.var
    def formatted_holidays(self) -> list[dict]:
        return [
            {"id": h.id, "date": h.date.strftime("%d-%m-%Y"), "name": h.name}
            for h in self.national_holidays
        ]
