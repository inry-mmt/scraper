# encoding: utf-8

import requests
from bs4 import BeautifulSoup as bsp
import time

class ArticleData():
    ''' 一記事分のタイトルと本文 '''

    def __init__(self):
        self.title = ''
        self.description = ''

def main():
    root_url = 'http://www.asahi.com'
    url = 'http://www.asahi.com/politics/list/'
    res = requests.get(url)

    soup = bsp(res.text, 'lxml')

    urls = get_articles_urls(soup,
        (
            ('ul', 'List'),
            ('li', ''),
        )
        , link_class="SW"
    )

    article_datas = []
    for u in urls:
        time.sleep(2)   # 過アクセス防止

        if not (u.startswith('http') and u.startswith('https')):
            u = root_url + u

        res = requests.get(u)
        soup = bsp(res.text, 'lxml')

        article_data = ArticleData()
        article_data.title = get_title(soup,
            (
                ('div', 'ArticleTitle'),
                ('div', 'Title'),
                ('h1', ''),
            )
        )
        article_data.description = get_description(soup,
            (
                ('div', 'ArticleText'),
                ('p', ''),
            )
        )

        article_datas.append(article_data)
        print('fetched from {}'.format(u))

    for a in article_datas:
        print(a.title)
        print(a.description)
        print('\n-+-+-+-+-+-+-+-\n')


def get_articles_urls(soup, wrapper=(('div', ''),), link_class=''):
    '''
    与えられたsoupオブジェクトから記事にあたる要素を抜き出し、
    link_classのclassを持ったa要素からurlを抜き出し、リストにして返す

    args:
        soup:
            beautifulsoupオブジェクト

        wrapper:
            二重リスト（タプル）
            仮に対象が
            <ul class="article_links_list">
                <li class="article_link_container">
                    <div class="article_link_wrapper">
                        <a href="**" class="link">リンク先１</a>
                    </div>
                </li>
                <li class="article_link_container">
                    <div class="article_link_wrapper">
                        <a href="**" class="link">リンク先２</a>
                    </div>
                </li>
            </ul>
            という構造になっていた時は
            (
                ('ul', 'article_links_list'),
                ('li', 'article_link_container'),
                ('div', 'article_link_wrapper'),
            )
            というように上から指定する
            classの指定がない場合には空欄で
            (
                ('li', ''),
                ('div', ''),
            )
            というようにする

        link_class:
            ほしいURLへのリンクになるa要素が持っているclass
            特に指定しない時は空欄

    returns:
        urlのリスト
    '''

    containers = [soup]
    for w in wrapper:
        try:
            element = w[0]
            classname = w[1]
        except:
            raise ValueError('each wrapper needs "element name" and "class name"')

        # 上位から順にたどっていく
        # 最後に残ったものが<a>の直上（直上が指定されていれば）
        new_container = []
        for s in containers:
            if classname:
                new_container.extend(s.find_all(element, class_=classname))
            else:
                new_container.extend(s.find_all(element))

        del containers
        containers = new_container

    # a要素を取得
    links = []
    for c in containers:
        if link_class:
            links.extend(c.find_all('a', class_=link_class))
        else:
            links.extend(c.find_all('a'))

    # a要素からリンク先urlを取得
    urls = []
    for l in links:
        urls.append(l.attrs['href'])

    return urls


def get_title(soup, wrapper=(('h1', ''),)):
    '''
    記事ページからタイトルにあたる部分を抜き出す

    args:
        soup:
            beautifulsoupオブジェクト

        wrapper:
            求めるものが
            <div class="title_wrapper">
                <h1 class="title">タイトル</h1>
            </div>
            のような構造の時は
            (
                ('div', 'title_wrapper'),
                ('h1', 'title'),
            )
            で取得する。

    returns:
        タイトルのテキスト（strings)
    '''

    container = soup
    for w in wrapper:
        try:
            element = w[0]
            classname = w[1]
        except:
            raise ValueError('each wrapper needs "element name" and "class name"')

        if classname:
            container = container.find(element, class_=classname)
        else:
            container = container.find(element)

    return container.text


def get_description(soup, wrapper=(('div', ''),)):
    '''
    記事ページから本文にあたる部分を抜き出す
    複数あった場合は見つかった順に連結する
    '''

    descs = [soup]
    for w in wrapper:
        try:
            element = w[0]
            classname = w[1]
        except:
            raise ValueError('each wrapper needs "element name" and "class name"')

        new_descs = []
        for d in descs:
            if classname:
                new_descs.extend(d.find_all(element, classname))
            else:
                new_descs.extend(d.find_all(element))

        del descs
        descs = new_descs

    desc_text = ''
    for d in descs:
        desc_text += d.text

    return desc_text

if __name__ == '__main__':
    main()
