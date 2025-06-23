import os

import httpx
from dotenv import load_dotenv

from models.press import Press


async def create_press(data: Press):
    load_dotenv()
    base_url = os.getenv("CORE_API_URL")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            base_url+'/company',
            json={
                "name": data.name,
                "description": data.description,
                "profileImageUrl": data.profile_image_url,
                "signatureColor": data.signature_color,
            }
        )
        return response.json()