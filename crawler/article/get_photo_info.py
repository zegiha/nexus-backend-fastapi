def get_photo_info(soup):
    img_url = None
    img_desc = None

    photo_span = soup.select('span.end_photo_org')
    for span in photo_span:
        img_tag = span.select_one('img')
        desc_tag = span.select_one('em.img_desc')

        if img_tag and img_tag.get('src'):
            img_url = img_tag.get('src')
            if img_url is None:
                img_url = img_tag.get('data-src')

        if desc_tag:
            img_desc = desc_tag.get_text(strip=True)

    return [img_url, img_desc]