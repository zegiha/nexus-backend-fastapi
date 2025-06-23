import os

import httpx
from dotenv import load_dotenv


async def get_press_id(press_name: str):
    async with httpx.AsyncClient() as client:
        load_dotenv()
        base_url = os.getenv("CORE_API_URL")
        press_res = (await client.get(
            base_url+'/company/info/'+press_name
        )).json()
        if 'message' in press_res and 'Company does not exist' in press_res['message']:
            return None
        return press_res['uuid']