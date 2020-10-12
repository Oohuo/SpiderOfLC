#爬取Leetcode题目列表获得QUESTION_ID（题目ID）、TITLE（标题）、TITLESLUG（请求标题）、DIFFICULTY（难度等级）、FRONTEND（前端ID）、PAID（是否付费题目）

import http.cookiejar as cookielib
import urllib.request

import emoji
import requests
import json
import datetime
import pymysql

#开始请求问题列表
from docutils.parsers import null

url="https://leetcode-cn.com/api/problems/all/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
cookies = {
    'cookie': '_uab_collina=159184635745193904444315; csrftoken=MbBXVJUmcjYOLderbCL5D4VaWaTB5gSgt3DTgGc6TA5BkWNbvurUJKOM5ljTBnEm; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzk4MjE4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYXV0aF9iYWNrZW5kcy5QaG9uZUF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY3NDM0ODlmMDhmOTFhNjM3MjI0MmNlOWMxMWQ5YjJjMGUxYmQxOWY0ZDAyOTc4ZmI3ODc3NjJlYThjMzIwZTIiLCJpZCI6Mzk4MjE4LCJlbWFpbCI6Im9vb2h1b0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im9vaHVvIiwidXNlcl9zbHVnIjoib29odW8iLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS1jbi5jb20vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy9haWVyYnVkZS9hdmF0YXJfMTU1MTM1MTcwNS5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiX3RpbWVzdGFtcCI6MTYwMDc2NzI5MC44MTY5NDN9.LPi0UyODHCmk7nNiuBtSQy4_OmV2O0oEFxab6FofJfA'}
questions = requests.get(url, headers=headers,cookies=cookies)

#格式化请求内容为JSON
questions_json = json.loads(questions.text)

#抽取问题列表
questions_list = questions_json['stat_status_pairs']


# 打开数据库连接
db = pymysql.connect("localhost","root","11","leetcodespyder" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

#循环遍历题目信息
for question_info in questions_list:
    # print(question_info['stat']['question_id'])
    # print(question_info['stat']['question__title'])
    # print(question_info['stat']['question__title_slug'])
    # print(question_info['difficulty']['level'])
    # print(question_info['paid_only'])
    # print(question_info['stat']['frontend_question_id'])

    # SQL 插入语句
    sql = "INSERT INTO question_copy(QUESTION_ID,TITLE,TITLESLUG,DIFFICULTY,PAID,FRONTEND) VALUES ("
    sql = sql + str(question_info['stat']['question_id'])+', '
    sql = sql + "\'"+  emoji.demojize(str(question_info['stat']['question__title']).replace("'", "’"))+ "\', "
    sql = sql + "\'"+ question_info['stat']['question__title_slug']+ "\', "
    sql = sql + str(question_info['difficulty']['level'])+ ", "
    sql = sql + "\'"+ str(question_info['paid_only'])+ "\', "
    sql = sql + "\'"+question_info['stat']['frontend_question_id']+ "\')"
    # print(sql)
    try:
        cursor.execute(sql)
        db.commit()
        # selectSQL = "select * from question where FRONTEND="
        # selectSQL = selectSQL + str("'"+question_info['stat']['frontend_question_id']+"'") + '; '
        # cursor.execute(selectSQL)
        # # 提交到数据库执行
        # results = cursor.fetchall()
        # if results == null:
        #     cursor.execute(sql)
        #     # 提交到数据库执行
        #     db.commit()
        #     print("QUESTION_ID:",question_info['stat']['question_id'],"\033[1;32;40mSUCCESS!\033[0m")
    except:
        # 如果发生错误则回滚
        db.rollback()
        print(sql)
        print("QUESTION_ID:",question_info['stat']['question_id'],"\033[1;31;40mERROR!\033[0m")

# 关闭数据库连接
db.close()
