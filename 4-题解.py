# 建立IP代理池，对题解按语言和耗时进行爬取，暴力遍历题解的APIURL实现
import json
import re

import emoji
import pymysql
import requests
import pymysql
import threading
import re
import time
from queue import Queue
from DBUtils.PooledDB import PooledDB
from jieba import xrange


def mysql_connection():
    maxconnections = 10  # 最大连接数
    pool = PooledDB(
        pymysql,
        maxconnections,
        host='localhost',
        user='root',
        port=3306,
        passwd='11',
        db='leetcodespyder',
        use_unicode=True)
    return pool


def get_proxy():
    return requests.get("http://118.24.52.95/get/").json()


def delete_proxy(proxy):
    requests.get("http://118.24.52.95/delete/?proxy={}".format(proxy))


# 打开数据库连接
dbPoolConnect = mysql_connection().connection()
db = pymysql.connect("localhost", "root", "11", "leetcodespyder", charset="utf8mb4", use_unicode=True)

# 使用cursor()方法获取操作游标
dbPoolCursor = dbPoolConnect.cursor()
cursor = dbPoolConnect.cursor()
select_id_list = []
select_language_list = []
# SQL 查询语句
# select_id_sql = "SELECT QUESTION_ID FROM QUESTION WHERE PAID != \"True\" "
select_id_sql = "SELECT titleSlug,QUESTION_ID,translatedtitle FROM enterprise where isthereasolution =0 "
try:
    # 执行SQL语句
    cursor.execute(select_id_sql)
    # 获取所有记录列表
    select_id_list = cursor.fetchall()
    cursor.execute("select * from language ")
    select_language_list = cursor.fetchall()
except:
    print("Error: unable to fetch data")
print(len(select_id_list))

highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
# 请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    , 'authority': 'leetcode-cn.com'
    , 'origin': 'https://leetcode-cn.com'
    , 'referer': 'https://leetcode-cn.com/problems/'}
payloadData = {"operationName": "questionSolutionArticles",
               "variables": {"questionSlug": "add-two-numbers", "first": 10, "skip": 0, "orderBy": "MOST_UPVOTE",
                             "tagSlugs": ["java"], "userInput": ""},
               "query": "query questionSolutionArticles($questionSlug: String!, $skip: Int, $first: Int, $orderBy: SolutionArticleOrderBy, $userInput: String, $tagSlugs: [String!]) {\n  questionSolutionArticles(questionSlug: $questionSlug, skip: $skip, first: $first, orderBy: $orderBy, userInput: $userInput, tagSlugs: $tagSlugs) {\n    totalNum\n    edges {\n      node {\n        ...solutionArticle\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment solutionArticle on SolutionArticleNode {\n  uuid\n  title\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n    __typename\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    __typename\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    profile {\n      userAvatar\n      userSlug\n      realName\n      __typename\n    }\n    __typename\n  }\n  summary\n  topic {\n    id\n    commentCount\n    viewCount\n    __typename\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n    __typename\n  }\n  __typename\n}\n"}
headers_ = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    , 'authority': 'leetcode-cn.com'
    , 'content-type': 'application/json'}

payloadData_ = {"operationName": "solutionDetailArticle",
                "variables": {"slug": "liang-shu-xiang-jia-by-gpe3dbjds1", "orderBy": "DEFAULT"},
                "query": "query solutionDetailArticle($slug: String!, $orderBy: SolutionArticleOrderBy!) {\n  solutionArticle(slug: $slug, orderBy: $orderBy) {\n    ...solutionArticle\n    content\n    question {\n      questionTitleSlug\n      __typename\n    }\n    position\n    next {\n      slug\n      title\n      __typename\n    }\n    prev {\n      slug\n      title\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment solutionArticle on SolutionArticleNode {\n  uuid\n  title\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n    __typename\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    __typename\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    profile {\n      userAvatar\n      userSlug\n      realName\n      __typename\n    }\n    __typename\n  }\n  summary\n  topic {\n    id\n    commentCount\n    viewCount\n    __typename\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n    __typename\n  }\n  __typename\n}\n"}
cookies = {
    'cookie': '_uab_collina=159184635745193904444315; csrftoken=MbBXVJUmcjYOLderbCL5D4VaWaTB5gSgt3DTgGc6TA5BkWNbvurUJKOM5ljTBnEm; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzk4MjE4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYXV0aF9iYWNrZW5kcy5QaG9uZUF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY3NDM0ODlmMDhmOTFhNjM3MjI0MmNlOWMxMWQ5YjJjMGUxYmQxOWY0ZDAyOTc4ZmI3ODc3NjJlYThjMzIwZTIiLCJpZCI6Mzk4MjE4LCJlbWFpbCI6Im9vb2h1b0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im9vaHVvIiwidXNlcl9zbHVnIjoib29odW8iLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS1jbi5jb20vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy9haWVyYnVkZS9hdmF0YXJfMTU1MTM1MTcwNS5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiX3RpbWVzdGFtcCI6MTYwMDc2NzI5MC44MTY5NDN9.LPi0UyODHCmk7nNiuBtSQy4_OmV2O0oEFxab6FofJfA'}
solution_url = "https://leetcode-cn.com/graphql/"
# 获取设定代理节点
# proxies = {'http': ''}
# proxy = get_proxy().decode()
# proxies["http"] = proxy
# 有效solution计数
nums = 0

proxyList = [{"check_count": 367, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "61.135.185.118:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 4032, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "182.61.62.74:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "182.32.162.205:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 8, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "61.135.185.172:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.47.8.187:3128",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 1, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "116.196.85.150:3128", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.64.82:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "42.238.86.196:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 4048, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "180.97.34.35:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 76, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "61.135.185.153:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "60.5.254.169:8081",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.156.35:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 1, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:45",
              "proxy": "61.135.185.90:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.27.150:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.103.57:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "125.108.122.214:9000",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 318, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:46",
              "proxy": "61.135.185.112:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.155.13:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.99.15:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 1, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:55",
              "proxy": "61.135.185.68:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.220.95.44:10174",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 4065, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:55",
              "proxy": "180.97.33.144:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 31474, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "180.149.145.132:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 38072, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "117.185.16.31:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "36.249.109.27:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.115.94:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 4051, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "180.97.33.93:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.27.241:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 320, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "61.135.185.111:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 1, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:46",
              "proxy": "112.95.188.29:9000", "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.42.128.10:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 256, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "220.181.77.210:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "113.128.121.161:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.220.95.55:9400",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.159.217:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 2, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "61.135.185.176:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 96, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "61.135.185.156:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 4020, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "202.108.23.174:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "203.189.89.153:8080",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 4050, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "180.97.33.94:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.163.32.88:3128",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.103.140:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 8740, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "211.137.52.158:8080", "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.48.7:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.42.128.250:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.220.48.30:9000",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.152.13:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.206.72.230:9000",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.85.238.227:3128",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.158.137:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.220.49.9:9000",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "117.141.155.241:53281",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.43.153.19:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "113.161.58.255:8080",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.89.236:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 10, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:47",
              "proxy": "59.120.117.244:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 383, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:47",
              "proxy": "140.207.229.171:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "38.91.100.171:3128",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.42.123.217:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 4014, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:47",
              "proxy": "183.232.231.239:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.103.104:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.169.166.61:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 71, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "61.135.185.160:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.42.128.10:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.121.98:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "36.248.129.44:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.55.114.205:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 31473, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "180.97.33.66:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "122.4.53.86:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 319, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:46",
              "proxy": "61.135.185.103:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.155.33:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.149.136.99:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.189.2:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 4083, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "180.97.33.212:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.121.98:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "119.57.156.90:53281",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "124.205.155.150:9090",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.95.162:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.81.144.199:9000",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 9817, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "183.232.231.76:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "222.162.1.108:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.106.223.134:80",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.186.80:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.188.104:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 538, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:46",
              "proxy": "61.135.169.121:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "125.108.64.149:9000",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.186.243:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "113.194.31.221:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 956, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "220.181.111.37:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.115.94:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "42.238.86.250:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "223.82.106.253:3128",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 20, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "61.135.185.31:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "182.105.201.40:9000",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "171.35.175.87:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "42.7.31.233:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.152.131:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "113.195.147.93:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.185.69:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.191.209:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "120.83.100.243:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.48.197:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 663, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:56",
              "proxy": "222.74.202.228:9999", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "112.111.217.49:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.154.74:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.220.166.15:9000",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "36.248.133.24:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.185.92:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.57.210.164:3128",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "112.47.3.53:3128",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "120.83.100.243:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "112.111.217.69:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.42.122.171:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.117.65:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.158.147:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.32.243:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "14.115.106.204:808",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 30, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:05",
              "proxy": "113.214.13.1:1080", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 38039, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:56",
              "proxy": "117.185.17.16:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.103.180:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 295, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:56",
              "proxy": "61.135.185.152:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.157.217:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.81.146.28:9000",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "123.163.117.65:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 23, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "61.135.185.20:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "60.167.159.224:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.81.150.71:9000",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "222.90.110.194:8080",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.153.16:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 2, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:14",
              "proxy": "58.220.95.30:10174", "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 4027, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:55",
              "proxy": "183.232.231.133:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.220.95.79:10000",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.191.90:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.81.148.43:9000",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "60.184.205.240:3000",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "211.21.120.163:8080",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.186.222:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "61.135.185.78:80",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.43.57.18:9999",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.85.47:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.89.75:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 823, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:05",
              "proxy": "222.74.202.227:9999", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 295, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "61.135.185.12:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "106.3.45.16:58080",
              "region": "", "source": "freeProxy01", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.89.86.85:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.253.158.76:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "58.220.95.90:9401",
              "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "1.196.177.114:9999",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.189.24:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 3, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:32:45",
              "proxy": "61.135.185.38:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "39.81.150.158:9000",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "113.194.31.221:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "122.136.212.132:53281",
              "region": "", "source": "freeProxy05", "type": ""},
             {"check_count": 4007, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "202.108.22.5:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 6, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:14",
              "proxy": "203.184.132.229:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "175.43.57.18:12219",
              "region": "", "source": "freeProxy04", "type": ""},
             {"check_count": 4015, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "183.232.232.69:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "27.43.186.158:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 36773, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "111.206.37.244:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.89.51:9999",
              "region": "", "source": "freeProxy07", "type": ""},
             {"check_count": 13148, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "221.180.170.104:8080", "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 0, "fail_count": 0, "last_status": "", "last_time": "", "proxy": "49.70.94.157:9999",
              "region": "", "source": "freeProxy14", "type": ""},
             {"check_count": 4078, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "180.97.33.92:80", "region": "", "source": "freeProxy09", "type": ""},
             {"check_count": 4078, "fail_count": 0, "last_status": 1, "last_time": "2020-10-03 01:33:06",
              "proxy": "180.97.33.78:80", "region": "", "source": "freeProxy09", "type": ""}]


def cutList(LLL, time):
    result = [[] for _ in range(time)]
    for item in LLL:
        if len(result[0]) < 16:
            result[0].append(item)
        elif len(result[1]) < 16:
            result[1].append(item)
        elif len(result[2]) < 16:
            result[2].append(item)
        elif len(result[3]) < 16:
            result[3].append(item)
        elif len(result[4]) < 16:
            result[4].append(item)
        elif len(result[5]) < 16:
            result[5].append(item)
        elif len(result[6]) < 16:
            result[6].append(item)
        elif len(result[7]) < 16:
            result[7].append(item)
        elif len(result[8]) < 16:
            result[8].append(item)
        elif len(result[9]) < 16:
            result[9].append(item)
        elif len(result[10]) < 16:
            result[10].append(item)
        elif len(result[11]) < 16:
            result[11].append(item)
        elif len(result[12]) < 16:
            result[12].append(item)
        elif len(result[13]) < 16:
            result[13].append(item)
        elif len(result[14]) < 16:
            result[14].append(item)
        elif len(result[15]) < 16:
            result[15].append(item)
        elif len(result[16]) < 16:
            result[16].append(item)
        elif len(result[17]) < 16:
            result[17].append(item)
        elif len(result[18]) < 16:
            result[18].append(item)
        elif len(result[19]) < 16:
            result[19].append(item)
        elif len(result[20]) < 16:
            result[20].append(item)
        elif len(result[21]) < 16:
            result[21].append(item)
        elif len(result[22]) < 16:
            result[22].append(item)
        elif len(result[23]) < 16:
            result[23].append(item)
        elif len(result[24]) < 16:
            result[24].append(item)
        elif len(result[25]) < 16:
            result[25].append(item)
        elif len(result[26]) < 16:
            result[26].append(item)
        elif len(result[27]) < 16:
            result[27].append(item)
        elif len(result[28]) < 16:
            result[28].append(item)
        elif len(result[29]) < 16:
            result[29].append(item)
        elif len(result[30]) < 16:
            result[30].append(item)
        elif len(result[31]) < 16:
            result[31].append(item)
        elif len(result[32]) < 16:
            result[32].append(item)
        elif len(result[33]) < 16:
            result[33].append(item)
        elif len(result[34]) < 16:
            result[34].append(item)
        elif len(result[35]) < 16:
            result[35].append(item)
        elif len(result[36]) < 16:
            result[36].append(item)
        elif len(result[37]) < 16:
            result[37].append(item)
        elif len(result[38]) < 16:
            result[38].append(item)
        elif len(result[39]) < 16:
            result[39].append(item)
        elif len(result[40]) < 16:
            result[40].append(item)
        elif len(result[41]) < 16:
            result[41].append(item)
        elif len(result[42]) < 16:
            result[42].append(item)
        elif len(result[43]) < 16:
            result[43].append(item)
        elif len(result[44]) < 16:
            result[44].append(item)
        elif len(result[45]) < 16:
            result[45].append(item)
        elif len(result[46]) < 16:
            result[46].append(item)
        elif len(result[47]) < 16:
            result[47].append(item)
        elif len(result[48]) < 16:
            result[48].append(item)
        else:
            result[49].append(item)
    return result


cut = cutList(select_id_list, 50)

conn = mysql_connection().connection()
cursor = conn.cursor()
def spiderLC(start, end):

    global nums
    ac = int(start)
    qwer = cut[ac]
    for titleSlug in qwer:
        for lang in select_language_list:
            # 问题循环
            # 语言循环
            payloadData["variables"]["tagSlugs"] = lang[1]
            payloadData["variables"]["questionSlug"] = titleSlug[0]
            payloadData["variables"]["first"] = 10
            payloadData["variables"]["skip"] = 0
            payloadData["variables"]["orderBy"] = 'MOST_UPVOTE'

            # 根据题目获取点赞最多的题解 10*
            solution_res = \
                json.loads(requests.post(solution_url, json=payloadData, headers=headers, cookies=cookies).text)[
                    'data'][
                    'questionSolutionArticles']['edges']
            times = 0
            # 根据slug获取详细题解
            for solution in solution_res:
                times += 1
                # print(solution['node']['slug'])
                payloadData_["variables"]["slug"] = solution['node']['slug']
                retry_count = 3
                for proxy_ in proxyList:
                    try:
                        solutionDetailsJson = json.loads(
                            requests.post(solution_url, json=payloadData_, headers=headers_, cookies=cookies,
                                          proxies={"http": "http://{}".format(proxy_)}).text)
                        break
                    except Exception:
                        delete_proxy(proxy_)
                        continue
                solutionDetails = solutionDetailsJson['data']['solutionArticle']
                solution_sql = "INSERT INTO enterprisesolution(QUESTION_ID,TITLE,SLUG,SUMMARY,LANGUAGE_ID,QUE_SOLUTION,CONTENT,QUESTIONTITLESLUG,translatedtitle) VALUES ("
                solution_sql = solution_sql + "\'" + str(titleSlug[1]) + "\', "
                solution_sql = solution_sql + "\'" + emoji.demojize(
                    str(solutionDetails['title']).replace("'", "’")) + "\', "
                solution_sql = solution_sql + "\'" + str(solutionDetails['slug']) + "\', "
                solution_sql = solution_sql + "\'" + emoji.demojize(
                    str(solutionDetails['summary']).replace("'", "’")) + "\', "
                solution_sql = solution_sql + str(lang[0]) + ", "
                tijie = emoji.demojize(str(solutionDetails['content']).replace("'", "’"))
                solution_sql = solution_sql + "\'" + tijie + "\', "
                solution_sql = solution_sql + "\'" + tijie + "\', "
                solution_sql = solution_sql + "\'" + str(solutionDetails['question']['questionTitleSlug']) + "\', "
                solution_sql = solution_sql + "\'" + str(titleSlug[2]) + "\')"
                try:
                    # 执行sql语句
                    cursor.execute(solution_sql)
                    # 提交到数据库执行
                    dbPoolConnect.commit()
                    # print("\033[1;32;40mSUCCESS!\033[0m")
                    nums = nums + 1
                    print("线程", end, "操作:", titleSlug[1], '-', times, str(lang[0]), ":插入题解表成功!")
                except Exception as e:
                    # 如果发生错误则回滚
                    dbPoolConnect.rollback()
                    print(titleSlug[1], '-', times, "\033[1;31;40mERROR!      ERROR!      ERROR!\033[0m", 'SQL执行有误,原因:',
                          e)
                    print("solution_sql:", solution_sql)
                finally:
                    cursor.close()
                    conn.close()

            if times > 0:
                updateQuestionSQL = "UPDATE ENTERPRISE SET ISTHEREASOLUTION=ISTHEREASOLUTION+1 WHERE QUESTION_ID ="
                updateQuestionSQL = updateQuestionSQL + str(titleSlug[1]) + ';'
                print(updateQuestionSQL)
                cursor.execute(updateQuestionSQL)
                dbPoolConnect.commit()
                print("线程", end, "操作:", '更新企业题表成功', titleSlug[1], "题的解题数为：", times)


def poolS(thread_num):
    threads = []

    times = 0
    for i in range(thread_num):
        t = threading.Thread(target=spiderLC, args=(times, times))
        times += 1
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


class MyThread(threading.Thread):

    def __init__(self, name, count, exec_object):
        threading.Thread.__init__(self)
        self.name = name
        self.count = count
        self.exec_object = exec_object

    def run(self):
        while self.count >= 0:
            count = count - 1
            self.exec_object.execFunc(count)


thread1 = MyThread('MyThread1', 3, spiderLC(1, 1))
thread2 = MyThread('MyThread2', 5, spiderLC(2, 2))
thread1.start()
thread2.start()
thread1.join()  # join方法 执行完thread1的方法才继续主线程
thread2.join()
poolS(16)  # 开10个线程
# 关闭数据库连接
db.close()
print(nums)
