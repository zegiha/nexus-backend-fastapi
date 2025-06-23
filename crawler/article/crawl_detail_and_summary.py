from datetime import datetime
from sqlalchemy.orm import Session

from crawler.article.crawl_detail import crawling_detail
from crawler.article.send_article import send_article
from models.rawArticle import RawArticle

async def crawl_detail_and_summary(
        raw_data,
        create_date: datetime,
        is_headline: bool,
        press: str,
        db: Session,
):
    if raw_data is None:
        return None

    result = []

    for li in raw_data.find_all('li'):
        for dl in li.find_all('dl'):
            if not dl:
                continue

            dt_list = dl.findAll('dt')
            dt_photo = None
            dt_title = None
            if len(dt_list) < 2:
                dt_title = dt_list[0]
            else:
                dt_photo = dt_list[0]
                dt_title = dt_list[1]

            article = {}

            if dt_photo:
                a = dt_photo.find('a')
                img = a.find('img')
                if img and img.get('src'):
                    article['summary_img'] = img['src']

            if dt_title:
                a = dt_title.find('a')
                if a:
                    article['title'] = a.get_text(strip=True)
                    article['originalArticleUrl'] = a['href']
                    is_duplicate = db.query(RawArticle).filter(RawArticle.original_article_url == article['originalArticleUrl']).first()
                    if is_duplicate:
                        continue
                    detail = await crawling_detail(article['originalArticleUrl'])
                    if detail == {}:
                        detail = await crawling_detail(article['originalArticleUrl'])
                    if detail is None:
                        detail = {}
                    article.update(detail)


            if all(key in article for key in ['contents', 'title', 'originalArticleUrl']):
                new_article = RawArticle(
                    title=article['title'],
                    contents=article['contents'],
                    category=article['category'],
                    original_article_url=article['originalArticleUrl'],
                    summary_img_url=article.get('summary_img') or None,
                    img_url=article.get('img_url') or None,
                    img_desc=article.get('img_desc') or None,
                    video_url=article.get('video_url') or None,
                    create_date=create_date,
                )
                db.add(new_article)
                db.commit()
                db.refresh(new_article)

                try:
                    print('sending', flush=True)
                    await send_article(new_article, is_headline, press)
                    print('sended', flush=True)
                except Exception as e:
                    print(f"Error during sending: {e}", flush=True)

                result.append(article)

    return result