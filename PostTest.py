import json
import threading
import time

import emoji
import pymysql
import requests
from bs4 import BeautifulSoup
from jieba import xrange

headers_ = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    , 'authority': 'leetcode-cn.com'
    , 'content-type': 'application/json'}

payloadData_ = {"operationName": "solutionDetailArticle",
                "variables": {"slug": "liang-shu-xiang-jia-by-gpe3dbjds1", "orderBy": "DEFAULT"},
                "query": "query solutionDetailArticle($slug: String!, $orderBy: SolutionArticleOrderBy!) {\n  solutionArticle(slug: $slug, orderBy: $orderBy) {\n    ...solutionArticle\n    content\n    question {\n      questionTitleSlug\n      __typename\n    }\n    position\n    next {\n      slug\n      title\n      __typename\n    }\n    prev {\n      slug\n      title\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment solutionArticle on SolutionArticleNode {\n  uuid\n  title\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n    __typename\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    __typename\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    profile {\n      userAvatar\n      userSlug\n      realName\n      __typename\n    }\n    __typename\n  }\n  summary\n  topic {\n    id\n    commentCount\n    viewCount\n    __typename\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n    __typename\n  }\n  __typename\n}\n"}
cookies = {
    'cookie': '_uab_collina=159184635745193904444315; csrftoken=MbBXVJUmcjYOLderbCL5D4VaWaTB5gSgt3DTgGc6TA5BkWNbvurUJKOM5ljTBnEm; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzk4MjE4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYXV0aF9iYWNrZW5kcy5QaG9uZUF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY3NDM0ODlmMDhmOTFhNjM3MjI0MmNlOWMxMWQ5YjJjMGUxYmQxOWY0ZDAyOTc4ZmI3ODc3NjJlYThjMzIwZTIiLCJpZCI6Mzk4MjE4LCJlbWFpbCI6Im9vb2h1b0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im9vaHVvIiwidXNlcl9zbHVnIjoib29odW8iLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS1jbi5jb20vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy9haWVyYnVkZS9hdmF0YXJfMTU1MTM1MTcwNS5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiX3RpbWVzdGFtcCI6MTYwMDc2NzI5MC44MTY5NDN9.LPi0UyODHCmk7nNiuBtSQy4_OmV2O0oEFxab6FofJfA'}
# solutionDetailsJson = json.loads(requests.post('https://leetcode-cn.com/graphql/', json=payloadData_, headers=headers_, cookies=cookies).text)
# print(solutionDetailsJson)
#
# str = "123456'789'"
# print(str)
# str1 = str.replace("'","")
# print(str1)


# print(emoji.emojize('Python is :thumbs_up:'))
# print(emoji.demojize('🙉'))


import requests

# def get_proxy():
#     return requests.get("http://118.24.52.95/get_all/").json()
#
# def delete_proxy(proxy):
#     requests.get("http://118.24.52.95/delete/?proxy={}".format(proxy))
#
# # your spider code
#
# if __name__ == '__main__':
#
#     # ....
#     retry_count = 5
#     allProxy = get_proxy()
#     for proxy in allProxy:
#
#         proxies={"http": "http://{}".format(proxy['proxy'])}
#         print(proxy['proxy'])
#         while retry_count > 0:
#             try:
#                 html = requests.post('https://leetcode-cn.com/graphql/', json=payloadData_, headers=headers_, cookies=cookies, proxies={"http": "http://{}".format(proxy)})
#                 # 使用代理访问
#                 # print(html)
#             except Exception:
#                 retry_count -= 1
#                 # 删除代理池中代理
#                 delete_proxy(proxy)
#                 break

# def baidu_search(start_num,end_num,keyWord):
#     '''
#     采集百度搜索结果的标题
#     :param start_num: 起始页码
#     :param end_num: 结束页码
#     :param keyWord: 搜索的关键词
#     '''
#     for i in range(start_num,end_num):
#         url = 'https://www.baidu.com/s?wd=%s&pn=%d'% (keyWord,i*10)
#         headers = {
#             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
#         }
#         r = requests.get(url,headers=headers).text   # 获取源码
#         soup = BeautifulSoup(r,'lxml')  # BeautifulSoup 解析
#         result = soup.select('div.result.c-container > h3 > a')  # 通过 css selector 定位查询结果所在元素，返回结果是个列表
#         for i in result:
#             title = i.text    # 通过 .text 方法获取元素内的文本
#             print(title)
#
#

L = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
     32, 33, 34, 35, 36, 37, 38, 39, 40]


def cut(LLL, time):
    result = [[] for _ in range(time)]
    for item in L:
        if len(result[0]) < 10:
            result[0].append(item)
        elif len(result[1]) < 10:
            result[1].append(item)
        elif len(result[2]) < 10:
            result[2].append(item)
        elif len(result[3]) < 10:
            result[3].append(item)
        elif len(result[4]) < 10:
            result[4].append(item)
        elif len(result[5]) < 10:
            result[5].append(item)
        elif len(result[6]) < 10:
            result[6].append(item)
        elif len(result[7]) < 10:
            result[7].append(item)
        elif len(result[8]) < 10:
            result[8].append(item)
        else:
            result[9].append(item)
    return result


print(cut(L,10))
#
result = [[], [], [], [], [], [], [], [], [], []]
for item in L:
    if len(result[0]) < 10:
        result[0].append(item)
    elif len(result[1]) < 10:
        result[1].append(item)
    elif len(result[2]) < 10:
        result[2].append(item)
    elif len(result[3]) < 10:
        result[3].append(item)
    elif len(result[4]) < 10:
        result[4].append(item)
    elif len(result[5]) < 10:
        result[5].append(item)
    elif len(result[6]) < 10:
        result[6].append(item)
    elif len(result[7]) < 10:
        result[7].append(item)
    elif len(result[8]) < 10:
        result[8].append(item)
    else:
        result[9].append(item)
print(result)


def baidu_dx(all_num,thread_num,keyWord):
    '''
    多线程采集百度搜索结果的标题
    :param all_num: 要采集的总页数
    :param thread_num: 要开启的线程数
    :param keyWord: 搜索的关键词
    '''
    per_num = int(all_num / thread_num)  # 每个线程处理的任务数量
    threads = []  # 开启的线程放到一个列表

    for i in range(thread_num):
        t = threading.Thread(target=baidu_search, args=(i*per_num,i*per_num+per_num,keyWord))
        threads.append(t)

    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()

if __name__ == '__main__':
    start = time.time()
    baidu_dx(200,10,'python')  # 采集200页的数据，开10个线程，搜索关键词是 python
    end = time.time()
    print('\n采集总共耗时：' + str(int(end - start)) + ' 秒')
