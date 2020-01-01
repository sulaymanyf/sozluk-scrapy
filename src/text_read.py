import pandas as pd
from requests import RequestException
from sqlalchemy import create_engine
from sqlalchemy.types import String
from sqlalchemy.orm import sessionmaker
import importlib, sys
import re
import time
from lxml import etree
import brotli
import requests
from collections import Counter

engine = create_engine('mysql+pymysql://root:Admin1234@localhost/sozluk')


def open_file():
    file = pd.read_csv('./data/ecdict.csv', encoding="utf-8")
    print(file.shape)
    pd.io.sql.to_sql(frame=file, name='eng_chinese', con=engine, index=False, if_exists='append')

    file = ''
    # with open('./data/牛津高阶双解.txt', 'r') as f:
    #     for line in f.readlines():
    #         file += line
    #
    # print(len(file))
    # # file.replace("/\s+<\/?>/", '</>')
    # num =re.sub('\s+<\/?>', '</>', file, count=0)
    # # num =re.sub('\n', '', num, count=0)
    # print(num)

    # df = pd.read_table('./data/牛津高阶双解.txt', engine='c', header=None, sep='\r')
    # arr = df.values.copy()
    # fd2 = pd.DataFrame(arr).values()
    # fd2.to_csv("out2.csv", index=None, header=None)


words = []


def get_word():
    file = pd.read_csv('./data/ecdict.csv', encoding="utf-8")
    print(file['word'])
    for word in file['word']:
        word = str(word).replace("'", "")
        word = str(word).replace("-", "")
        words.append(word)

    # with open('./data/word.txt', 'w') as f:
    #     for word in file['word']:
    # words.append(word)
    # f.write(str(word))
    # f.write(',')


def tureng_word(word):
    headers = {
        'authority': 'tureng.com',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'sec-fetch-user': '?1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'referer': 'https://tureng.com/en/turkish-english',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,tr;q=0.7',
        'cookie': '__cfduid=d3898876e40074583493b86b5ba679e751577716357; VFRVREM%3d=ZW4%3d; VFRESUNUSU9OQVJZ=ZW50cg%3d%3d; _ga=GA1.2.831908032.1577716363; _gid=GA1.2.1257173107.1577716363; pId=vnetc4b47646-b898-4790-827a-c2a42bf41ad2; __gads=ID=7dbc7dd27aee26de:T=1577716372:S=ALNI_MaM61kQF7fX-FxPcJYNcFsvbYp6Qw; __gfp_64b=eMqFHYA23zMu.pWD5LYPvZ93RmK3pXflS_BzqjfW6wT.R7; THI=hello=637133172118562333&word=637133177688751805; GED_PLAYLIST_ACTIVITY=W3sidSI6InM3NW4iLCJ0c2wiOjE1Nzc3MTc0NzMsIm52IjowLCJ1cHQiOjE1Nzc3MTczNjksImx0IjoxNTc3NzE3NDY3fSx7InUiOiJYU243IiwidHNsIjoxNTc3NzE3NDczLCJudiI6MCwidXB0IjoxNTc3NzE2ODEzLCJsdCI6MTU3NzcxNzM1MX1d',
    }

    try:
        # 获取网页内容，返回html数据
        response = requests.get('https://tureng.com/en/turkish-english/' + word, headers=headers)
        # 通过状态码判断是否获取成功
        if response.status_code == 200:
            # response.encoding = 'utf-8'
            print(response.headers)
            print(response.encoding)
            key = 'Content-Encoding'
            print(response.headers[key])
            print("-----------")
            if (key in response.headers and response.headers['Content-Encoding'] == 'br'):
                data = brotli.decompress(response.content)
                # data1 = data.decode('utf-8')
                # print(data1)
                print(data)
                # return data1
                return data
            # print(response.text)
            return response.text
        return response.content.decode()
    except RequestException as e:
        return None
    # print(response.content.decode())


def get_table(text, kelime):
    kelimeler = []
    print("------kelime-" * 10)
    print(kelime)
    print("------kelime-" * 10)
    html = etree.HTML(text)
    html_table = html.xpath('//*[@id="englishResultsTable"]//tr')
    print(html_table)
    # html_table[0]
    for item in html_table:
        # /td/a/text()
        word = item.xpath('td/a/text()')
        # print(item.xpath('td/a/text()'))
        if (word != None) and (len(word) > 0):
            # print(word[0], word[1])
            if word[0] == kelime or word[0] == kelime+'-' or word[0] == '-'+kelime:
                kelimeler.append({"word": kelime, "turkish": word[1]})
    # word = html_table
    # # print(item.xpath('td/a/text()'))
    # if (word != None) and (len(word) > 0):
    #     # print(word[0], word[1])
    #     if word[0] == kelime:
    #         kelimeler.append({"word": kelime, "turkish": word[1]})
    print(kelimeler)
    return kelimeler


def get_sql_obj(wordss):
    if len(wordss) == 0:
        return
    turkish = ''
    kelime = ''
    for word in wordss:
        kelime = word['word']
        turkish += word.get('turkish') + ', '
    print(turkish)
    word_dict = {"word": kelime, "turkish": turkish}
    if word_dict['turkish'] == '':
        with open('./data/pro_word.txt', 'a') as f:
            f.write(wordss[0] + "\n")
            return
    return word_dict


if __name__ == '__main__':
    # open_file()
    get_word()
    for word in words:
        text = tureng_word(word)
        wordss = get_table(text, word)
        one_word = get_sql_obj(wordss)
        print(one_word)
        if one_word is not None:
            with open('./data/sql.txt', 'a', newline="\n") as f:
                sql = "UPDATE `sozluk`.`eng_chinese` t SET t.`turkish` = '{}' WHERE t.`id` = {}".format(
                    one_word.get('turkish'), 0)
                sql_word = {"sql": sql, 'word': word}
                f.write(sql_word.__str__() + "\n")

    # pd.read_table("./data/牛津高阶双解.txt", header=None, names=['id','word','chinese'], sep=" ")
    # ff = pd.DataFrame(pd.read_table("./data/牛津高阶双解.txt",nrows=100, sep=r'<\/?>', engine='python', header=None).values.reshape(-1, 2)).dropna()
    # print(ff)
    # pd.DataFrame（pd.read_csv（'test.csv'，header = None）.values.reshape（-1, 2））
#     ff.to_sql('Writers', engine, index=True)
#     # pd.io.sql.to_sql(file, 'Writers', con=engine, if_exists='append', index=id)
