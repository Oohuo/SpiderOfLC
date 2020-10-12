# 添加问题题干、通过数、提交数、建立相似问题关系数据
import emoji
import pymysql
import http.cookiejar as cookielib
import urllib.request
import requests
import json

# import datetime

# 初始化可获取问题列表
from docutils.writers import null

question_list = []

# 打开数据库连接
db = pymysql.connect("localhost", "root", "11", "leetcodespyder")

# 使用cursor()方法获取操作游标
cursor = db.cursor()
# question_sql 查询语句获取非付费问题列表
question_sql = "SELECT QUESTION_ID, TITLESLUG ,TEANSLATEDCONTENT FROM QUESTION_copy  "
# question_sql = "SELECT QUESTION_ID, TITLESLUG,translatedtitle FROM QUESTION  "
# question_sql = "SELECT QUESTION_ID, TITLESLUG FROM enterprise WHERE SOLUTION_NUM IS NULL "
try:
    # 执行question_sql语句
    cursor.execute(question_sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        if row[2]=='None' or row[2]=='' or row[2]==None:
            # 问题信息列表
            question = []
            question.append(row[0])
            question.append(row[1])
            # 问题列表
            question_list.append(question)
    print("问题列表请求成功!")
except:
    print("请求失败!")

# print(question_list)

# 请求头信息
url = "https://leetcode-cn.com/graphql"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
payloadData = {"operationName": "questionData", "variables": {"titleSlug": "two-sum"},
               "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    __typename\n  }\n}\n"}
payloadData_ = {"operationName": "solutionCount", "variables": {"questionSlug": "intersection-of-three-sorted-arrays"},
                "query": "query solutionCount($questionSlug: String!) {\n  solutionNum(questionSlug: $questionSlug)\n}\n"}
cookies = {
    'cookie': '_uab_collina=159184635745193904444315; csrftoken=MbBXVJUmcjYOLderbCL5D4VaWaTB5gSgt3DTgGc6TA5BkWNbvurUJKOM5ljTBnEm; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMzk4MjE4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYXV0aF9iYWNrZW5kcy5QaG9uZUF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY3NDM0ODlmMDhmOTFhNjM3MjI0MmNlOWMxMWQ5YjJjMGUxYmQxOWY0ZDAyOTc4ZmI3ODc3NjJlYThjMzIwZTIiLCJpZCI6Mzk4MjE4LCJlbWFpbCI6Im9vb2h1b0BnbWFpbC5jb20iLCJ1c2VybmFtZSI6Im9vaHVvIiwidXNlcl9zbHVnIjoib29odW8iLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS1jbi5jb20vYWxpeXVuLWxjLXVwbG9hZC91c2Vycy9haWVyYnVkZS9hdmF0YXJfMTU1MTM1MTcwNS5wbmciLCJwaG9uZV92ZXJpZmllZCI6dHJ1ZSwiX3RpbWVzdGFtcCI6MTYwMDc2NzI5MC44MTY5NDN9.LPi0UyODHCmk7nNiuBtSQy4_OmV2O0oEFxab6FofJfA'}
# 开始循环遍历请求题目详细信息
for question in question_list:
    # print("开始请求获取问题：", question[1], "问题编号：", question[0])

    # 设定请求标题
    payloadData["variables"]["titleSlug"] = question[1]
    payloadData_["variables"]["questionSlug"] = question[1]
    # 请求数据
    question_data = requests.post(url, json=payloadData, headers=headers, cookies=cookies)
    questions_json = json.loads(question_data.text)

    question_data_ = requests.post(url, json=payloadData_, headers=headers, cookies=cookies)
    questions_json_ = json.loads(question_data_.text)
    # print(questions_json)

    # 输出题目信息
    # print(questions_json["data"]["question"]["translatedTitle"])
    # print(questions_json["data"]["question"]["content"])
    # print(questions_json["data"]["question"]["translatedContent"])
    # print(json.loads(questions_json["data"]["question"]["stats"])["totalAcceptedRaw"])
    # print(json.loads(questions_json["data"]["question"]["stats"])["totalSubmissionRaw"])

    # 生成信息插入SQL语句
    question_sql = "UPDATE QUESTION_copy SET "
    # question_sql = "UPDATE enterprise SET "
    # if content exist "xx' xx" ,maybe print a bug.
    question_sql = question_sql + "CONTENT=" + "\'" + str(questions_json["data"]["question"]["content"]).replace('\'',
                                                                                                                 '‘') + '\', '
    question_sql = question_sql + "TRANSLATEDTITLE=" + "\"" + str(
        questions_json["data"]["question"]["translatedTitle"]) + '\", '

    question_sql = question_sql + "TEANSLATEDCONTENT=" + "\'" + emoji.demojize(str(
         questions_json["data"]["question"]["translatedContent"]).replace("'", "’")) + '\', '

    question_sql = question_sql + "ACCEPT=" + str(
        json.loads(questions_json["data"]["question"]["stats"])["totalAcceptedRaw"]) + ', '

    question_sql = question_sql + "SOLUTION_NUM=" + str(json.loads(str(questions_json_["data"]["solutionNum"]))) + ', '

    question_sql = question_sql + "SUBMISSION=" + str(
        json.loads(questions_json["data"]["question"]["stats"])["totalSubmissionRaw"]) + ' '

    question_sql = question_sql + "WHERE QUESTION_ID=" + str(question[0])
    # print ("信息更新SQL语句：", question_sql)
    # selectSQL = "select TRANSLATEDTITLE from question where QUESTION_ID="
    # selectSQL = selectSQL + str(question[0]) + '; '
    try:
        # # 执行sql语句
        # cursor.execute(selectSQL)
        # # 提交到数据库执行
        # results = cursor.fetchall()
        # print(results[0][0])
        # if results[0][0] == '' or results[0][0] =='None':
            # 执行sql语句
        cursor.execute(question_sql)
            # 提交到数据库执行
        db.commit()
            # print(question_sql)
        print(question[0],"更新","\033[1;32;40mSUCCESS!\033[0m")
    except:
        # 如果发生错误则回滚
        db.rollback()
        print("信息更新SQL语句：", question_sql)
        print("question更新", str(question[0]), "\033[1;31;40mERROR!\033[0m")

    # # 抽取相似问题列表
    # similar_questions = json.loads(questions_json["data"]["question"]["similarQuestions"])
    # for i in similar_questions:
    #     # 根据相似问题请求标题获取该问题ID
    #     select_sql = "select QUESTION_ID from question where TITLESLUG = " + "\"" + i["titleSlug"] + "\""
    #     # print("select_sql:",select_sql)
    #     try:
    #         # 执行question_sql语句
    #         cursor.execute(select_sql)
    #         # 获取所有记录列表
    #         results = cursor.fetchall()
    #         # print("\033[1;32;40mselect_SUCCESS!\033[0m")
    #         for row in results:
    #             similar_question = []
    #             similar_question.append(row[0])
    #             # print(row[0])
    #             for j in similar_question:
    #                 similar_sql = "INSERT INTO SIMILAR(QUE_ID,SIM_ID) VALUES ("
    #                 similar_sql = similar_sql + str(question[0]) + ", "
    #                 similar_sql = similar_sql + str(j) + ")"
    #                 # print ("相似题目插入SQL语句：", similar_sql)
    #                 try:
    #                     # 执行sql语句
    #                     cursor.execute(similar_sql)
    #                     # 提交到数据库执行
    #                     db.commit()
    #                     # print("question插入", "\033[1;32;40mSUCCESS!!\033[0m")
    #                 except:
    #                     # 如果发生错误则回滚
    #                     db.rollback()
    #                     print("similar插入", "\033[1;31;40mERROR!!\033[0m")
    #     except:
    #         # 如果发生错误则回滚
    #         db.rollback()
    #         print("\033[1;31;40mselect_ERROR!\033[0m")
    # print("QUESTION_ID:", question[0], "\033[1;32;40m请求完毕!!!!!\033[0m")

# 关闭数据库连接
db.close()

print("爬取结束！")
