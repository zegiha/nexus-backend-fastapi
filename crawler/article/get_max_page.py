def get_max_page(paging):
    pages = paging.select('a')
    select_page = paging.select_one('strong')
    if pages[-1].get_text(strip=True) == '다음':
        # print(f'returning contents: {pages[-2].get_text(strip=True)}')
        res = pages[-2].get_text(strip=True)
    else:
        # print(f'returning contents: {pages[-1].get_text(strip=True)}')
        res = pages[-1].get_text(strip=True)
    return max(int(res), int(select_page.get_text(strip=True)))
