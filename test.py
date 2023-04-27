import re
import re

# The SQL text with output results
sql_text = """
SELECT * FROM table1;

 id | name 
----+------
  1 | foo  
  2 | bar  

SELECT * FROM table2;

 id | value 
----+-------
  1 |  100  
  2 |  200  
"""

# The regular expression pattern to match the output results
import re

# 保存查询结果到字符串中
query_result = """
create table test_byte (col char(4 byte));
insert into test_byte values ('1234');
insert into test_byte values ('12345');
ERROR: value too large for column "public"."test_byte"."col" (actual:5, maximum:4) insert into test_byte values ('一');
insert into test_byte values ('一二三');
ERROR: value too large for column "public"."test_byte"."col" (actual:9, maximum:4) select col, length(col) from test_byte;
COL | LENGTH 
------+-------- 
1234 | 4
"""

# 使用正则表达式匹配查询结果中的表头和表格部分，并替换为空字符串
cleaned_result = re.sub(r'\s*\w+\s*\|\s*\w+\s*\n|-*[+]-*()', '', query_result)
# cleaned_result = re.sub(r'\+[-]+\+\n\|\s*\w+\s*\|(.*?\n)*?\+[-]+\+', '', query_result)

# 输出清理后的结果
print(cleaned_result)



# def replace_values(sql):
#     pattern = r'values\s+\(\s*([\d\-\.:\',\s]+)\s*\)(?:(?:\s*,\s*\(\s*)([\d\-\.:\',\s]+)(?:\s*\))'
#     pattern = r"values\s*\((.*?)\)\s*(?:,\s*\((.*?)\))*"
#     pattern = r"VALUES\s*\(((?:[^(),]+|\((?P>content)\))*)\)"
#     pattern = r"\(([^)]*)\)"
#     matches = re.findall(pattern, sql, re.I)
#     print(matches)
#     # 遍历匹配结果，进行替换
#     for match in matches:
#         values_str = match.strip()
#         values_list = values_str.split(',')
#         new_values = []
#         for value in values_list:
#             if re.match(r'^\d+$', value.strip()):
#                 new_values.append('numint')
#             elif re.match(r'^\d+\.\d+$', value.strip()):
#                 new_values.append('numfl')
#             elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', value.strip()):
#                 new_values.append('numtime')
#             else:
#                 new_values.append(value)
#         new_values_str = ', '.join(new_values)
#         sql = sql.replace(values_str, new_values_str)
#
#     return sql
#
#
# sql = "INSERT INTO table_name (col1, col2, col3) VALUES (1, 2.3, '2023-04-24 12:34:56'), (1, 2, 3), (2, 2, 2), (4,5,6)"
# new_sql = replace_values(sql)
# print(new_sql)
#
#
#
#
# def parse_sql(sql):
#     sql = sql.lower()
#     result = {'table': '', 'columns': [], 'aliases': {}}
#
#     if 'insert' in sql:
#         table_match = re.search(r'insert\s+into\s+(\w+)', sql)
#         if table_match:
#             result['table'] = table_match.group(1)
#
#         columns_match = re.search(r'\((.*?)\)', sql)
#         if columns_match:
#             columns = columns_match.group(1).split(',')
#             result['columns'] = [col.strip() for col in columns]
#
#     elif 'update' in sql:
#         table_match = re.search(r'update\s+(\w+)', sql)
#         if table_match:
#             result['table'] = table_match.group(1)
#
#         columns_match = re.findall(r'(\w+)\s*=\s*(\w+)', sql)
#         if columns_match:
#             for col, alias in columns_match:
#                 result['columns'].append(col)
#                 result['aliases'][col] = alias
#
#     return result
#
#
# def split_sqls(text):
#     sql = []
#     pattern1 = r"\\set SQLTERM "
#     match = re.match(pattern1, text, re.I)
#     if match:
#         char = ";"
#         texts = text.split("\n")
#         s = ""
#         i = 0
#         while i < len(texts):
#             if texts[i].startswith(r"\set SQLTERM "):
#                 char = texts[i][13]
#                 print(char)
#                 s = s + texts[i] + "\n"
#                 i = i + 1
#                 while char not in texts[i] and i < len(texts):
#                     s = s + texts[i] + "\n"
#                     i = i + 1
#                 s = s + texts[i] + "\n"
#                 sql.append(s)
#                 s = ""
#             else:
#                 if char in texts[i]:
#                     s = s + texts[i] + "\n"
#                     i = i + 1
#                 else:
#                     s = s + texts[i] + "\n"
#                     i = i + 1
#                     sql.append(s)
#                     s = ""
#     else:
#         texts = text.split(";")
#         for i in range(len(texts)):
#             sql.append(texts[i])
#     return sql
#
#
# def replace_name(text):
#     sqls = split_sqls(text)
#     col_num = 0
#     table_num = 0
#     table_total = []
#     for i in range(len(sqls)):
#         table, alias = extract_table_name(sqls[i])
#         for j in range(len(table)):
#             if table[j] not in table_total:
#                 cre_stmt = createSQL.get(table[j])
#                 columns = extract_column_names(cre_stmt)
#                 for x in range(len(columns)):
#                     if "." + columns[x] in text:
#                         pattern = table[j] + r"\s+AS\s+(\w+)"
#                         matches = re.match(pattern, text, re.I)
#                         if matches[0] + "." + columns[x] in text:
#                             pattern = r"\b" + re.escape(matches[0] + "." + columns[x]) + r"\b"
#                             text = re.sub(pattern, "col" + str(col_num), text)
#                         else:
#                             pattern = r"\b" + re.escape(table[j] + "." + columns[x]) + r"\b"
#                             text = re.sub(pattern, "col" + str(col_num), text)
#                     else:
#                         pattern = r"\b" + re.escape(columns[x]) + r"\b"
#                         text = re.sub(pattern, "col" + str(col_num), text)
#                     col_num = col_num + 1
#                 pattern = r"\b" + re.escape(table[j]) + r"\b"
#                 text = re.sub(pattern, "t" + str(table_num), text)
#                 table_num = table_num + 1
#                 table_total.append(table[j])
#     return text
#
#
# def extract_column_names(create_table_statement):
#     # 使用正则表达式匹配建表语句中的列名
#     pattern = r"\((.*)?\);"
#     match = re.search(pattern, create_table_statement, re.DOTALL)
#     if match:
#         column_definitions = match.group(1)
#         column = [column.split()[0] for column in column_definitions.split(",")]
#         column_names = []
#         for i in range(len(column)):
#             if "(" in column[i] and ")" in column[i]:
#                 column_names.append(column[i])
#             elif "(" in column[i] or ")" in column[i]:
#                 continue
#             else:
#                 column_names.append(column[i])
#         return column_names
#     else:
#         return None
#
# # 示例
#
# def remove_space(text):
#     text = re.sub(r'\n', ' ', text)
#     text = re.sub(r'\s', ' ', text)
#     text = re.sub(r'\\t', ' ', text)
#     text = re.sub(r' +', ' ', text)
#     return text
#
#
# def replace_num(text):
#     text = re.sub(r'(?<!t)(?<!col)\b\d+\.\d+\b', 'numfl', text)
#     text = re.sub(r'(?<!t)(?<!col)\b\d+\b', 'numint', text)
#     return text
#
#
# def replace_integers(text, replacement="numint"):
#     pattern = r'(?<!t)(?<!col)\b\d+\b'
#     return re.sub(pattern, replacement, text)
#
#
# text = "123 t123 col123 (123) 456 t456 col456 (456)"
# result = replace_integers(text)
# print(result)
#
# # UPDATE weather SET temp_lo = temp_lo+1, temp_hi = temp_lo+15, prcp = DEFAULT
# #   WHERE city = 'San Francisco' AND date = '2003-07-03';
# sql = open('./a.txt', 'r', encoding='utf-8').read()
# # text = replace_name(sql)
# # print(text)
# # print(replace_num(text))
#
