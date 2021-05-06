from bs4 import BeautifulSoup, SoupStrainer
from custom_types import NewsSource, Rating
from pickle import dump, HIGHEST_PROTOCOL
from requests import get
from tqdm import tqdm
from typing import Optional
from urllib.parse import urljoin

ALL_SIDES_BASE_URL = 'https://www.allsides.com'


def get_rating_helper(rating: str) -> Rating:
    if rating == 'Left':
        return Rating.LEFT
    elif rating == 'Lean Left':
        return Rating.LEAN_LEFT
    elif rating == 'Center':
        return Rating.CENTER
    elif rating == 'Lean Right':
        return Rating.LEAN_RIGHT
    elif rating == 'Right':
        return Rating.RIGHT
    elif rating == 'Mixed':
        return Rating.MIXED
    else:
        raise ValueError(f'An unknown rating "{rating}" was encountered')


def process_news_source(news_source) -> Optional[NewsSource]:
    # News source's name is found in the first "td" tag
    name = news_source.find('td').a.text
    # Each rating begins with the following prefix string: "AllSides Media Bias Rating: "
    rating = get_rating_helper(news_source.find('img')['alt'][28:])
    # Find URL for this news source by using a proxy (inner) page
    proxy_link = news_source.find('a')['href']
    proxy_html = get(urljoin(ALL_SIDES_BASE_URL, proxy_link)).text
    proxy_bs = BeautifulSoup(proxy_html, 'html.parser', parse_only=SoupStrainer(class_='dynamic-grid'))
    link = proxy_bs.find('a')
    if link is not None:
        return NewsSource(name, rating, link['href'])
    else:
        return None


def main() -> None:
    # Load cached copy of HTML table from AllSides Media Bias Ratings:
    # https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B2%5D=2&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&title=
    with open('media_bias_table.html') as html:
        bs = BeautifulSoup(html, 'html.parser')
    # Split table by rows without first result (table header)
    news_sources = bs('tr')[1:]
    print(f'Found {len(news_sources)} news source candidates')
    # Process each news source and save results
    results = []
    for news_source in tqdm(news_sources, total=len(news_sources)):
        result = process_news_source(news_source)
        if result is not None:
            results.append(result)
    print(f'Only {len(results)} news sources were actually valid')
    with open('news_sources.pickle', 'wb') as outfile:
        dump(results, outfile, protocol=HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()