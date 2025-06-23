import httpx

async def get_video_url(soup):
    video_info_tag = soup.select_one('div._VOD_PLAYER_WRAP')
    if video_info_tag:
        video_id = video_info_tag.get('data-video-id')
        video_key = video_info_tag.get('data-inkey')

        video_json_query_url = f'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{video_id}?key={video_key}&sid=2006&nonce=1746276897832&devt=html5_pc&prv=N&aup=N&stpb=N&cpl=ko_KR&env=real&lc=ko_KR&adi=%5B%7B%22adSystem%22%3A%22null%22%7D%5D&adu=%2F'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(video_json_query_url, headers=headers, timeout=None)

                if res.status_code != 200:
                    return None

                video_url = None
                max_bitrate = 0
                max_width = 0
                video_json = res.json()
                for v in video_json['videos']['list']:
                    if v['encodingOption']['width'] >= max_width and v['bitrate']['video'] > max_bitrate:
                        max_bitrate = v['bitrate']['video']
                        max_width = v['width']
                        video_url = v['source']

                return video_url
            except httpx.RequestError as _:
                return None
    else:
        return None