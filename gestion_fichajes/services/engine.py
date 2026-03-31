import asyncio
import random
from datetime import datetime, date, time, timedelta
from typing import Optional
import reflex as rx
from sqlmodel import Session, select
from gestion_fichajes.models.model import User, GlobalSettings, Vacation, NationalHoliday
from gestion_fichajes.services.clock_in import ATRService
from zoneinfo import ZoneInfo

async def run_engine_iteration():
    """Single iteration of the clocking engine."""
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    today = now.date()
    weekday = today.weekday()

    with rx.session() as session:
        # 1. Get Global Settings
        settings = session.exec(select(GlobalSettings)).first()
        if not settings:
            settings = GlobalSettings(margin_minutes=5)
            session.add(settings)
            session.commit()
            session.refresh(settings)
        
        margin = settings.margin_minutes

        # 2. Get National Holiday for today
        holiday = session.exec(select(NationalHoliday).where(NationalHoliday.date == today)).first()
        if holiday:
            return # No clocking on holidays

        # 3. Process each active user
        users = session.exec(select(User).where(User.activo == True)).all()
        
        for user in users:
            # Skip if no person_id or no credentials
            if not user.person_id or not user.usuario or not user.contraseña:
                continue

            # a. Check if today is a work day
            work_days = [int(d) for d in user.work_days.split(",")] if user.work_days else []
            if weekday not in work_days:
                continue

            # b. Check for vacations
            is_vacation = session.exec(select(Vacation).where(
                Vacation.user_id == user.id,
                Vacation.date == today
            )).first()
            if is_vacation or user.vacaciones:
                continue

            # c. Generate Daily Offsets if needed
            if user.last_offset_date != today:
                user.today_offset_in_1 = random.randint(-margin, margin)
                user.today_offset_out_1 = random.randint(-margin, margin)
                user.today_offset_in_2 = random.randint(-margin, margin)
                user.today_offset_out_2 = random.randint(-margin, margin)
                user.last_offset_date = today
                session.add(user)
                session.commit()

            # d. Clocking Logic
            # Helper to combine date and time with offset and zero seconds
            def get_target(base_time: time, offset_min: int):
                if not base_time: return None
                dt = datetime.combine(today, base_time, tzinfo=ZoneInfo("Europe/Madrid"))
                target = dt + timedelta(minutes=offset_min)
                return target.replace(second=0, microsecond=0)

            target_in_1 = get_target(user.chin_1, user.today_offset_in_1)
            target_out_1 = get_target(user.chout_1, user.today_offset_out_1)
            target_in_2 = get_target(user.chin_2, user.today_offset_in_2) if user.chin_2 else None
            target_out_2 = get_target(user.chout_2, user.today_offset_out_2) if user.chout_2 else None

            service = ATRService(user.usuario, user.contraseña)

            # --- Shift 1 ---
            # Entry 1 (only if not already done today)
            if target_in_1 and now >= target_in_1 and now < (target_in_1 + timedelta(hours=2)):
                if user.active_checking_id is None and user.last_auto_in_1 != today:
                    print(f"Automatic Clock-In 1 for {user.nombre} at scheduled {target_in_1}")
                    # Usamos target_in_1 para el fichaje real en ATR
                    atr_id = await service.start_fichaje(user.person_id, target_in_1)
                    if atr_id:
                        user.active_checking_id = atr_id
                        user.last_auto_in_1 = today
                        session.add(user)
                        session.commit()

            # Exit 1 (only if there is an active session and not already exited today)
            if target_out_1 and now >= target_out_1:
                if user.active_checking_id is not None and user.last_auto_out_1 != today:
                    is_before_shift_2 = True
                    if target_in_2 and now >= target_in_2:
                        is_before_shift_2 = False
                    
                    if is_before_shift_2:
                        print(f"Automatic Clock-Out 1 for {user.nombre} at scheduled {target_out_1}")
                        res = await service.get_clock_ins(user.person_id, today.strftime("%Y-%m-%d"))
                        if res.get("success"):
                            rows = res.get("data", {}).get("rows", [])
                            open_session = next((r for r in rows if r.get("id") == user.active_checking_id), None)
                            if open_session:
                                # Usamos la hora de inicio real guardada en ATR para el PUT, y nuestro target_out para el fin
                                init_dt = datetime.fromisoformat(open_session["init_date"].replace("Z", "+00:00"))
                                success = await service.end_fichaje(user.active_checking_id, user.person_id, init_dt, target_out_1)
                                if success:
                                    user.active_checking_id = None
                                    user.last_auto_out_1 = today
                                    session.add(user)
                                    session.commit()

            # --- Shift 2 ---
            if not user.intensiva and target_in_2 and target_out_2:
                # Entry 2 (only if not already done today)
                if now >= target_in_2 and now < (target_in_2 + timedelta(hours=2)):
                    if user.active_checking_id is None and user.last_auto_in_2 != today:
                        print(f"Automatic Clock-In 2 for {user.nombre} at scheduled {target_in_2}")
                        atr_id = await service.start_fichaje(user.person_id, target_in_2)
                        if atr_id:
                            user.active_checking_id = atr_id
                            user.last_auto_in_2 = today
                            session.add(user)
                            session.commit()

                # Exit 2 (only if there is an active session and not already exited today)
                if now >= target_out_2:
                    if user.active_checking_id is not None and user.last_auto_out_2 != today:
                        res = await service.get_clock_ins(user.person_id, today.strftime("%Y-%m-%d"))
                        if res.get("success"):
                            rows = res.get("data", {}).get("rows", [])
                            open_session = next((r for r in rows if r.get("id") == user.active_checking_id), None)
                            if open_session:
                                init_dt = datetime.fromisoformat(open_session["init_date"].replace("Z", "+00:00"))
                                success = await service.end_fichaje(user.active_checking_id, user.person_id, init_dt, target_out_2)
                                if success:
                                    user.active_checking_id = None
                                    user.last_auto_out_2 = today
                                    session.add(user)
                                    session.commit()

async def daemon_loop():
    """Background loop that runs every minute."""
    print("Starting Clocking Engine Daemon...", flush=True)
    while True:
        try:
            await run_engine_iteration()
        except Exception as e:
            print(f"Error in Engine Iteration: {e}")
        # Wait for 1 minute
        await asyncio.sleep(60)
