import httpx
import asyncio
import json
from datetime import datetime, timezone
from typing import Optional

BASE_URL = "https://clientes.atrpresencia.com/api"


class ATRService:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.token: Optional[str] = None

    async def login(self) -> dict:
        """Login to ATR Presencia and return token and person_id."""
        url = f"{BASE_URL}/Auth/Login"
        payload = {"email": self.email, "password": self.password}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token", {}).get("accessToken")
                    person_id = data.get("person_id")
                    self.token = token
                    return {"success": True, "token": token, "person_id": person_id}
                return {"success": False, "error": f"Credenciales inválidas (Status: {response.status_code})"}
            except Exception as e:
                print(f"Error logging in to ATR: {e}")
                return {"success": False, "error": str(e)}

    async def start_fichaje(
        self, person_id: str, init_date: datetime, notes: str = ""
    ) -> Optional[int]:
        """Start a clock-in record in ATR Presencia. Returns the ID of the new record."""
        if not self.token:
            res = await self.login()
            if not res.get("success"):
                return None

        url = f"{BASE_URL}/checkingIn/Start"
        headers = {"Authorization": f"Bearer {self.token}"}
        # Aseguramos UTC y formato con Z
        init_date_utc = init_date.astimezone(timezone.utc)
        payload = {
            "person_id": person_id,
            "init_date": init_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": notes,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json()
                    # Si la respuesta es una lista, tomamos el primer elemento (según Postman a veces ocurre)
                    if isinstance(data, list) and len(data) > 0:
                        return data[0].get("id")
                    return data.get("id")
                return None
            except Exception as e:
                print(f"Error starting fichaje for {person_id}: {e}")
                return None

    async def end_fichaje(
        self, checking_id: int, person_id: str, init_date: datetime, end_date: datetime, notes: str = ""
    ) -> bool:
        """Close an existing clock-in record in ATR Presencia using its ID."""
        if not self.token:
            res = await self.login()
            if not res.get("success"):
                return False

        url = f"{BASE_URL}/checkingIn/{checking_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        # Aseguramos UTC y formato con Z
        init_utc = init_date.astimezone(timezone.utc)
        end_utc = end_date.astimezone(timezone.utc)
        payload = {
            "id": checking_id,
            "person_id": person_id,
            "init_date": init_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": notes,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, json=payload, headers=headers)
                return response.status_code in [200, 201, 204]
            except Exception as e:
                print(f"Error ending fichaje {checking_id}: {e}")
                return False

    async def create_fichaje(
        self, person_id: str, init_date: datetime, end_date: datetime, notes: str = ""
    ) -> bool:
        """Create a complete clock-in record (original method, kept for compatibility)."""
        if not self.token:
            res = await self.login()
            if not res.get("success"):
                return False

        url = f"{BASE_URL}/checkingIn"
        headers = {"Authorization": f"Bearer {self.token}"}
        # Aseguramos UTC y formato con Z
        init_utc = init_date.astimezone(timezone.utc)
        end_utc = end_date.astimezone(timezone.utc)
        payload = {
            "person_id": person_id,
            "init_date": init_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date": end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "notes": notes,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                return response.status_code in [200, 201]
            except Exception as e:
                print(f"Error creating fichaje for {person_id}: {e}")
                return False

    async def update_fichaje(self, target_id: int, payload: dict) -> bool:
        if not self.token:
            res = await self.login()
            if not res.get("success"):
                return False

        url = f"{BASE_URL}/checkingIn/{target_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, json=payload, headers=headers)
                return response.status_code in [200, 201, 204]
            except Exception as e:
                print(f"Error updating fichaje {target_id}: {e}")
                return False

    async def get_clock_ins(
        self, person_id: str, since_date: Optional[str] = None, until_date: Optional[str] = None
    ) -> dict:
        """Fetch clock-in history from ATR Presencia."""
        if not self.token:
            await self.login()

        url = f"{BASE_URL}/CheckingIn/GetAll"
        params = {
            "_page": 1,
            "_pageSize": 100,
            "person_id": person_id,
            "since_date": since_date if since_date and since_date != "null" else "",
            "until_date": until_date if until_date and until_date != "null" else "",
        }
        # Según documentación Postman: Authorization: Bearer <token>
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                return {"success": False, "error": f"API Error: {response.status_code} - {response.text}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
