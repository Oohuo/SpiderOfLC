# 爬取Leetcode题目列表获得QUESTION_ID（题目ID）、TITLE（标题）、TITLESLUG（请求标题）、DIFFICULTY（难度等级）、FRONTEND（前端ID）、PAID（是否付费题目）

import http.cookiejar as cookielib
import urllib.request
import requests
import json
import datetime
import pymysql
from pyasn1.compat.octets import null

enterprise = ['bytedance', 'huawei', 'microsoft', 'alibaba', 'tencent', 'google', 'amazon', 'toutiao', 'didi',
              'meituan', 'baidu', 'mi', 'vivo'];
# 开始请求问题列表
url = "https://leetcode-cn.com/graphql/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    , 'authority': 'leetcode-cn.com'
    , 'origin': 'https://leetcode-cn.com'
    , 'referer': 'https://leetcode-cn.com/company/bytedance/'}
payloadData = {"operationName": "companyTag", "variables": {"slug": "bytedance"},
               "query": "query companyTag($slug: String!) {\n  interviewCard(companySlug: $slug) {\n    id\n    isFavorite\n    isPremiumOnly\n    privilegeExpiresAt\n    __typename\n  }\n  interviewCompanyOptions(query: $slug) {\n    id\n    __typename\n  }\n  companyTag(slug: $slug) {\n    name\n    id\n    imgUrl\n    translatedName\n    frequencies\n    questions {\n      title\n      translatedTitle\n      titleSlug\n      questionId\n      stats\n      status\n      questionFrontendId\n      difficulty\n      frequencyTimePeriod\n      topicTags {\n        id\n        name\n        slug\n        translatedName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
cookies = {
    'cookie': '_uab_collina=159184635745193904444315; csrftoken=MbBXVJUmcjYOLderbCL5D4VaWaTB5gSgt3DTgGc6TA5BkWNbvurUJKOM5ljTBnEm; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzk4MjE4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYXV0aF9iYWNrZW5kcy5QaG9uZUF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY3NDM0ODlmMDhmOTFhNjM3MjI0MmNlOWMxMWQ5YjJjMGUxYmQxOWY0ZDAyOTc4ZmI3ODc3NjJlYThjMzIwZTIiLCJpZCI6Mzk4MjE4LCJlbWFpbCI6Im9vb2h1b0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im9vaHVvIiwidXNlcl9zbHVnIjoib29odW8iLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS1jbi5jb20vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy9haWVyYnVkZS9hdmF0YXJfMTU1MTM1MTcwNS5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiX3RpbWVzdGFtcCI6MTYwMDc2NzI5MC44MTY5NDN9.LPi0UyODHCmk7nNiuBtSQy4_OmV2O0oEFxab6FofJfA'}
# 开始循环遍历请求题目详细信息
for enter in enterprise:
    print("当前企业是：", enter)
    payloadData["variables"]["slug"] = enter
    question_data = requests.post(url, json=payloadData, headers=headers, cookies=cookies)
    questions_json = json.loads(question_data.text)
    for question in questions_json['data']['companyTag']['questions']:
        # print("开始请求获取问题：", question[1], "问题编号：", question[0])
        # 打开数据库连接
        db = pymysql.connect("localhost", "root", "11", "leetcodespyder")

        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        selectSQL = "select * from enterprise where QUESTION_ID="
        selectSQL = selectSQL + str(question['questionId']) + '; '
        try:
            # 执行sql语句
            cursor.execute(selectSQL)
            # 提交到数据库执行
            results = cursor.fetchall()
            if results != null:

                uSQL = "update enterprise set importance=importance+1 where QUESTION_ID="
                uSQL = uSQL + str(question['questionId']) + ';'
                cursor.execute(uSQL)
                # 提交到数据库执行
                db.commit()
                print('更新', str(question['questionId']), " importance success!")
            else:
                # SQL 插入语句
                sql = "INSERT INTO enterprise(QUESTION_ID,TITLE,TITLESLUG,TRANSLATEDTITLE,DIFFICULTY,PAID,FRONTEND) VALUES ("
                sql = sql + str(question['questionId']) + ', '
                sql = sql + "\'" + question['title'] + "\', "
                sql = sql + "\'" + question['titleSlug'] + "\', "
                sql = sql + "\'" + question['translatedTitle'] + "\', "
                sql = sql + "\'" + str(question['difficulty']) + "\', "
                sql = sql + "\'" + str(question['isPaidOnly']) + "\', "
                print(sql)
                try:
                    # 执行sql语句
                    cursor.execute(sql)
                    # 提交到数据库执行
                    db.commit()
                    print("QUESTION_ID:", question['questionId'], "\033[1;32;40mSUCCESS!\033[0m")
                except:
                    # 如果发生错误则回滚
                    db.rollback()
                    print(sql)
                    print("QUESTION_ID:", question['questionId'], "\033[1;31;40mERROR!\033[0m")

        except:
            # 如果发生错误则回滚
            db.rollback()
            print(sql)
            print("QUESTION_ID:", question['questionId'], "\033[1;31;40mERROR!\033[0m")

    # 关闭数据库连接
    db.close()
