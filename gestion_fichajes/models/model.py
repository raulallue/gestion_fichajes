import reflex as rx
from typing import Optional, List
from datetime import time, date as date_type
import sqlmodel


class User(rx.Model, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    nombre: str
    usuario: str
    contraseña: str
    person_id: Optional[str] = None  # ID vinculada a ATR Presencia
    work_days: str = "0,1,2,3,4"  # Lunes a Viernes por defecto
    vacaciones: bool = False
    intensiva: bool = True
    activo: bool = True
    chin_1: time
    chout_1: time
    chin_2: Optional[time] = None
    chout_2: Optional[time] = None
    rol: str = sqlmodel.Field(default="user")

    # Automatización
    active_checking_id: Optional[int] = None
    today_offset_in_1: int = sqlmodel.Field(default=0)
    today_offset_out_1: int = sqlmodel.Field(default=0)
    today_offset_in_2: int = sqlmodel.Field(default=0)
    today_offset_out_2: int = sqlmodel.Field(default=0)
    last_offset_date: Optional[date_type] = None
    
    # Historial de automatización (para evitar bucles)
    last_auto_in_1: Optional[date_type] = None
    last_auto_out_1: Optional[date_type] = None
    last_auto_in_2: Optional[date_type] = None
    last_auto_out_2: Optional[date_type] = None

    # Relación con vacaciones (días específicos)
    dias_vacaciones: List["Vacation"] = sqlmodel.Relationship(back_populates="user")


class Vacation(rx.Model, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    date: date_type
    user_id: int = sqlmodel.Field(foreign_key="user.id")
    description: Optional[str] = None

    user: Optional[User] = sqlmodel.Relationship(back_populates="dias_vacaciones")


class NationalHoliday(rx.Model, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    date: date_type = sqlmodel.Field(unique=True, index=True)
    name: str


class GlobalSettings(rx.Model, table=True):
    id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    margin_minutes: int = 5
