import asyncio
import bs4 as bs
import grequests
import datetime

from dataclasses import dataclass
from document import Document
from typing import Optional


@dataclass
class Post:
    url: str
    title: str
    date: Optional[datetime.date]
    link: Optional[str]

    async def from_url(url: str):
        '''Create a Post from a url.

        `url` is downloaded and parsed.
        '''
        # Throttle requests to not overload hackernews servers and
        # avoid ban.
        await asyncio.sleep(0.5)
        response = grequests.map([grequests.get(url)])[0]
        if response.status_code != 200:
            raise Exception(f'Failed to fetch {url}. Status {
                            response.status_code}')
        return Post.from_content(url, response.content)

    def from_content(url: str, content: str):
        '''Create a Post from a url and its content as an html string.'''
        content = bs.BeautifulSoup(content)

        title_elem = content.find('span', {'class': 'titleline'})
        title = ''
        link = None
        if title_elem is not None:
            title = str(title_elem.contents[0].string)
            link = title_elem.attrs.get('href', None)

        age_elem = content.find('span', {'class': 'age'})
        date = None
        if age_elem is not None:
            date = datetime.datetime.strptime(
                age_elem.attrs['title'], "%Y-%m-%dT%H:%M:%S").date()

        post = Post(
            url=url,
            title=title,
            date=date,
            link=link)
        return post

    def to_document(self) -> Document:
        date = None
        if self.date is not None:
            date = str(self.date)
        return Document(url=self.url,
                        title=self.title,
                        date=date)


def top_stories(date: Optional[datetime.date] = None) -> list[str]:
    '''
    Returns a url list of the top stories on Hacker News.
    '''
    if date is None:
        date = datetime.date.today()
    day_str = str(date)
    page = grequests.get(f'https://news.ycombinator.com/front?day={day_str}')
    response = grequests.map([page])[0]
    content = bs.BeautifulSoup(response.content)
    link_elems = content.find_all('a')
    links = map(lambda e: e.attrs['href'], link_elems)
    post_links = filter(lambda l: l.startswith('item?'), links)

    visited = set()
    unique = []
    for link in post_links:
        if link not in visited:
            visited.add(link)
            unique.append(f'https://news.ycombinator.com/{link}')
    return unique
