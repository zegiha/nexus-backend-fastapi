def get_category(soup):
    e = soup.select_one('li.Nlist_item._LNB_ITEM.is_active > a > span')
    if e is not None:
        return e.get_text(strip=True)
    else:
        return None