from crew.check_is_proper import check_is_proper
from crew.create_article import create_article
from crew.create_press import create_press
from crew.get_press_id import get_press_id
from crew.make_to_article import make_to_article
from crew.make_to_axios import make_to_axios
from crew.llm_instance import api_key
from models.article import MediaContent
from crawler.press.crawling_press import crawling_press
from models.raw_article_dto import RawArticleDTO


async def llm_processing(data: RawArticleDTO, is_headline: bool, press: str):
    print('checking press')
    press_id = await get_press_id(press)

    if not press_id:
        print('crawling press')
        press_data = await crawling_press(press)
        print('creating press')
        await create_press(press_data)
    else:
        print('rechecking press')
        press_id = await get_press_id(press)
        if not press_id:
            print('no press exception')
            return {'error': 'failed to create press'}

    try:
        print('start to generate article')
        print('get api key')
        if api_key is None: return {'error': 'no_api_key'}
        print('checking is proper article')
        is_proper_article = await check_is_proper(data)
        if not is_proper_article:
            return {'error': 'is_not_proper_article'}

        print('generating article')
        llm_processed_data = await make_to_axios(data)
        if llm_processed_data is None:
            return {'error': 'make_to_axios_error'}
        print('processing article')
        protocol_processed_data = await make_to_article(llm_processed_data)
        if protocol_processed_data is None:
            return {'error': 'make_to_article_error'}
    except Exception as e:
        err_str = str(e)

        print(err_str)

        # 🔍 529 상태 코드 또는 overloaded 메시지인 경우
        if '529' in err_str or 'overloaded' in err_str.lower() or 'AnthropicError' in err_str:
            print(f"[llm_processing] 과부하로 인한 실패 감지: {e}")
            return {'error': 'retry_later'}

        print(f"[llm_processing] 알 수 없는 LLM 처리 에러: {e}")
        return {'error': 'llm_processing_error', 'detail': err_str}

    if data.img_url is not None:
        print('processing article image')
        protocol_processed_data.append(MediaContent(
            type='media',
            mediaType='image',
            url=data.img_url,
            description=data.img_desc
        ))
    elif data.video_url is not None:
        print('processing article video')
        protocol_processed_data.append(MediaContent(
            type='media',
            mediaType='video',
            url=data.video_url,
            description=data.img_desc
        ))

    title = None
    print('processing article title')
    for v in protocol_processed_data:
        if v.type == 'subject':
            title = v.content
            break
    if title is None:
        return {'error': 'title is None'}

    summary_desc = None
    print('processing article summary')
    for v in protocol_processed_data:
        if v.type == 'description':
            summary_desc = v.content
            break
        elif v.type == 'list':
            summary_desc = v.contents[0].content
            break
    if summary_desc is None:
        return {'error': 'summary_desc is None'}

    print('making processed article')
    processed_article_data = {
        'title': title,
        'summary': summary_desc,
        'contents': protocol_processed_data,
    }

    print('creating article')
    await create_article(
        data,
        processed_article_data,
        is_headline,
        press_id
    )

    return protocol_processed_data