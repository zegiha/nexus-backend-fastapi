import requests
from bs4 import BeautifulSoup
import re
from const.press.get_press import get_press
from models.press import Press

async def crawling_press(press_name: str)->Press | str:
    oid_dict = get_press()
    press_oid = None
    for v in oid_dict:
        if v.get('press') == press_name:
            press_oid = v.get('oid')
            break

    if press_oid is None:
        return 'press is not exist'

    headers = {
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    res = requests.get('https://media.naver.com/press/'+press_oid, headers=headers, timeout=None)
    soup = BeautifulSoup(res.text, "html.parser")

    signature_color = re.search(
        r'color:\s*([^;]+)',
        soup.select_one('header.press_hd').get('style')
    )
    img_url = soup.select_one('a.press_hd_ci_image>img').get('src')
    desc = soup.select_one('p.press_hd_desc').get_text()

    return Press(
        name=press_name,
        description=desc,
        profile_image_url=img_url,
        signature_color=signature_color.group(1),
    )