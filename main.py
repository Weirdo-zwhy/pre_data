import requests
from bs4 import BeautifulSoup
import re
import json
import pre


path = "/Users/weirdozwhy/Desktop/testcase/"
idx = 0
x = ".txt"
pattern1 = r"(?i)create.*?;"
pattern2 = r'-[+-]*-'
keyword = ['CREATE', 'SELECT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'USE', 'BEGIN', 'COMMIT', 'ROLLBACK']
key1 = []
key2 = []
# 请求页面并获取 HTML 内容
url = 'https://help.kingbase.com.cn/v8/development/sql-plsql/sql/changes.html#id1'
prefu = 'https://help.kingbase.com.cn/v8/development/sql-plsql/sql/'
title = ''
createSQL = []
while not url is None:
    r = requests.get(url)
    demo = r.text
    soup = BeautifulSoup(demo, "html.parser")
    for t in soup.find_all('pre'):  # for循环遍历所有a标签，并把返回列表中的内容赋给t
        file_name = 'testcase' + str(idx) + x
        con = t.contents[1]
        if ';' not in con:
            continue
        else:
            text = pre.remove_comments(con)

    #
    #
    #         if re.match(pattern1, con, re.I):
    #             matches = re.findall(pattern2, con, re.I)
    #             sss = con
    #             if len(matches):
    #                 for i in range(len(matches)):
    #                     s1 = sss.find(matches[i])
    #                     s2 = sss.rfind(';', 0, s1)
    #                     index = -1
    #                     for char in keyword:
    #                         temp_index = sss.find(char, s1, len(sss))
    #                         if temp_index != -1:
    #                             if index == -1 or temp_index < index:
    #                                 index = temp_index
    #                     str1 = sss[:s2 + 1]
    #                     str2 = sss[index:]
    #                     sss = str1 + '\n' + str2
    #             with open(path + file_name, 'w', encoding='utf-8', errors='ignore') as fp:
    #                 fp.write(sss)
    #                 idx = idx + 1
    #             pattern3 = r'create.*?;'
    #             matches = re.findall(pattern3, sss)
    #             createSQL.append(matches)
    #         else:
    #             matches = re.findall(pattern2, con, re.I)
    #             sss = con
    #             if len(matches):
    #                 for i in range(len(matches)):
    #                     s1 = sss.find(matches[i])
    #                     s2 = sss.rfind(';', 0, s1)
    #                     index = -1
    #                     for char in keyword:
    #                         temp_index = sss.find(char, s1, len(sss))
    #                         if temp_index != -1:
    #                             if index == -1 or temp_index < index:
    #                                 index = temp_index
    #                     str1 = sss[:s2 + 1]
    #                     str2 = sss[index:]
    #                     sss = str1 + '\n' + str2
    #             with open(path + file_name, 'w', encoding='utf-8', errors='ignore') as fp:
    #                 fp.write(sss)
    #                 idx = idx + 1
    # next_link = soup.find("a", rel="next")
    # if next_link:
    #     url = prefu + next_link["href"]
    #     title = next_link["title"]
    # else:
    #     url = None

json_str = json.dumps(createSQL, ensure_ascii=False)

# 将JSON格式的字符串写入文件
with open("create.json", "w") as f:
    f.write(json_str)