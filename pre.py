import re
import os
import sqlparse
import json
from sqlparse.sql import Identifier, IdentifierList
import sql_metadata

keyword = ['CREATE', 'SELECT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'USE', 'BEGIN', 'COMMIT', 'ROLLBACK', 'MERGE',
           'INSERT', 'ANALYZE', '\\set', 'DECLARE', 'EXPLAIN', 'DEALLOCATE', 'COPY', 'ABORT', 'CALL', 'CLUSTER',
           'CLOSE', 'set',
           'CALL/EXEC', 'COMMENT', 'WITH', 'END', 'EXECUTE', 'PREPARE', 'LISTEN', 'NOTIFY']
createSQL = {}


def clean(text):
    text = remove_comments(text)
    text = remove_error_and_detail(text)
    text = pad_name(text)
    text = replace_word(text)
    text = remove_space(text)
    return text


def replace_word(text):
    text = replace_name(text)
    # text = replace_num(text)
    return text


def replace_num(text):
    text = re.sub(r'(?<!\bcol)\d+\.\d+|(?<!\bt)\d+\.\d+|(?<!\()\b\d+(\.\d+)?\b(?!\))', 'numfl', text)
    text = re.sub(r'(?<!\bcol)\d+|(?<!\bt)\d+|(?<!\()\b\d+\b(?!\))', 'numint', text)
    return text


def split_sqls(text):
    sql = []
    pattern1 = r"\\set\s+SQLTERM\s+([\$;/@])"
    match = re.findall(pattern1, text, re.I)
    print(match)
    if match:
        char = ";"
        texts = text.split("\n")
        s = ""
        i = 0
        exit = 0
        t = 0
        while i < len(texts):
            if r"\set SQLTERM" in texts[i]:
                char = texts[i][13]
            s = s + texts[i] + "\n"
            while char not in texts[i] and i < len(texts):
                i = i + 1
                if i == len(texts):
                    exit = 1
                    break
                t = 1
                s = s + texts[i] + "\n"
            if exit == 1:
                exit = 0
            else:
                if t == 1:
                    s = s + texts[i] + "\n"
                    t = 0
                sql.append(s)
                i = i + 1
                s = ""
    else:
        texts = text.split(";")
        for i in range(len(texts)):
            sql.append(texts[i])
    return sql


def find_name(sql):
    result = extract_create_statements(sql)
    if result:
        return result[0][len(result[0]) - 1]
    return None


def collect_create_sql(text):
    if text == "":
        return
    lines = text.split("\n")
    newline = []
    l = ""
    create = 0  # 判断是否有create语句，保存下来以便填充
    exit = 0
    char = ";"
    t = 0
    m = 0  # 特殊错误，最后一行或者最后一句没有；
    for i in range(len(lines)):
        if lines[i].split(" ")[0].upper() in keyword:
            if lines[i] != "INSERT 0 1":
                if lines[i].startswith(r"\set SQLTERM "):
                    char = lines[i][13]
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        newline.append(l)
                        i = i + 1
                    else:
                        exit = 0
                else:
                    if lines[i].startswith("CREATE") or lines[i].startswith("DECLARE"):
                        create = 1
                    if '...' in lines[i]:
                        exit = 1
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        if i == len(lines):
                            exit = 1
                            break
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        i = i + 1
                        newline.append(l)
                        if create == 1:
                            key = find_name(l)
                            if key not in createSQL.keys():
                                createSQL[key] = l
                                with open("create.json", "w") as f:
                                    json.dump(createSQL, f)
                    else:
                        exit = 0
                create = 0
                l = ""
            else:
                continue


def remove_detail(text):
    lines = text.split("\n")
    newline = []
    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        if lines[i].split(" ")[0].upper() in keyword:
            if lines[i] != "INSERT 0 1":
                if lines[i].startswith(r"\set SQLTERM "):
                    char = lines[i][13]
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        newline.append(l)
                        i = i + 1
                    else:
                        exit = 0
                else:
                    if lines[i].startswith("CREATE") or lines[i].startswith("DECLARE"):
                        create = 1
                    if '...' in lines[i]:
                        exit = 1
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        i = i + 1
                        newline.append(l)
                        if create == 1:
                            key = find_name(l)
                            if key not in createSQL.keys():
                                createSQL[key] = l
                                with open("create.json", "w") as f:
                                    json.dump(createSQL, f)
                    else:
                        exit = 0
                create = 0
                l = ""
            else:
                continue
        elif lines[i].startswith("ERROR:") or lines[i].startswith("DETAIL:") or lines[i].startswith("结果：") or lines[
            i].startswith("输出结果：") or lines[i].startswith("Result:") \
                or lines[i].startswith("输出：") or lines[i].startswith("LINE 1：") or lines[i].startswith("NOTICE: "):
            while lines[i].split(" ")[0] not in keyword:
                if "ERROR:" in lines[i]:
                    flag = 1
                l = l + lines[i]
                i = i + 1
                if i == len(lines):
                    break
            if flag == 1:
                newline.pop()
            l = ""
            flag = 0
        else:
            continue
    newlines = "\n".join(newline)
    return newlines


def remove_error_and_detail(text):
    lines = text.split("\n")
    newline = []
    l = ""
    flag = 0  # 是否有ERROR需要删除前一个sql语句
    create = 0  # 判断是否有create语句，保存下来以便填充
    exit = 0
    char = ";"
    t = 0
    for i in range(len(lines)):
        if lines[i].split(" ")[0].upper() in keyword:
            if lines[i] != "INSERT 0 1":
                if lines[i].startswith(r"\set SQLTERM "):
                    char = lines[i][13]
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        newline.append(l)
                        i = i + 1
                    else:
                        exit = 0
                else:
                    if lines[i].startswith("CREATE") or lines[i].startswith("DECLARE"):
                        create = 1
                    if '...' in lines[i]:
                        exit = 1
                    l = l + lines[i]
                    while char not in lines[i] and i < len(lines):
                        if '...' in lines[i]:
                            exit = 1
                            break
                        i = i + 1
                        t = 1
                        l = l + lines[i]
                    if t != 1:
                        t = 0
                    if exit == 0:
                        i = i + 1
                        newline.append(l)
                        if create == 1:
                            key = find_name(l)
                            if key not in createSQL.keys():
                                createSQL[key] = l
                                with open("create.json", "w") as f:
                                    json.dump(createSQL, f)
                    else:
                        exit = 0
                create = 0
                l = ""
            else:
                continue
        elif lines[i].startswith("ERROR:") or lines[i].startswith("DETAIL:") or lines[i].startswith("结果：") or lines[
            i].startswith("输出结果：") or lines[i].startswith("Result:") \
                or lines[i].startswith("输出：") or lines[i].startswith("LINE 1：") or lines[i].startswith("NOTICE: "):
            while lines[i].split(" ")[0] not in keyword:
                if "ERROR:" in lines[i]:
                    flag = 1
                l = l + lines[i]
                i = i + 1
                if i == len(lines):
                    break
            if flag == 1:
                newline.pop()
            l = ""
            flag = 0
        else:
            continue
    newlines = "\n".join(newline)
    return newlines


def remove_space(text):
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s', ' ', text)
    text = re.sub(r'\\t', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text


def remove_comments(text):
    text = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", text)
    # remove whole line -- and # comments
    lines = [line for line in text.splitlines() if not re.match("^\s*(--|#)", line)]
    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])
    q = ' '.join(q.split())
    return q


def replace_name(text):
    sqls = split_sqls(text)
    col_num = 0
    table_num = 0
    table_total = []
    for i in range(len(sqls)):
        if "set SQLTERM" in sqls[i]:
            continue
        table, alias = extract_table_name(sqls[i])
        for j in range(len(table)):
            print(table)
            if table[j] in table_total:
                continue
            if table[j] not in createSQL:
                continue
            cre_stmt = createSQL.get(table[j])
            print(cre_stmt)
            columns = extract_column_names(cre_stmt)
            if not columns:
                print(columns)
                continue
            for x in range(len(columns)):
                if "." + columns[x] in text:
                    pattern = table[j] + r"\s+AS\s+(\w+)"
                    matches = re.match(pattern, text, re.I)
                    if matches[0] + "." + columns[x] in text:
                        pattern = r"\b" + re.escape(matches[0] + "." + columns[x]) + r"\b"
                        text = re.sub(pattern, "col" + str(col_num), text)
                    else:
                        pattern = r"\b" + re.escape(table[j] + "." + columns[x]) + r"\b"
                        text = re.sub(pattern, "col" + str(col_num), text)
                else:
                    pattern = r"\b" + re.escape(columns[x]) + r"\b"
                    text = re.sub(pattern, "col" + str(col_num), text)
                col_num = col_num + 1
            text.replace(table[j], "t" + str(table_num))
            table_num = table_num + 1
        table_total.append(table)
    return text


def extract_column_names(create_table_statement):
    # 使用正则表达式匹配建表语句中的列名
    pattern = r"\((.*)?\);"
    print(create_table_statement)
    match = re.search(pattern, create_table_statement, re.DOTALL)
    if match:
        column_definitions = match.group(1)
        column = [column.split()[0] for column in column_definitions.split(",")]
        column_names = []
        for i in range(len(column)):
            if "(" in column[i] or ")" in column[i]:
                continue
            else:
                column_names.append(column[i])
        return column_names
    else:
        return None


def extract_create_statements(text):
    pattern = r'(?i)\bCREATE\s+(OR REPLACE\s+)?(GLOBAL\s+|LOCAL\s+|UNLOGGED\s+|DEFAULT\s+|UNIQUE\s+)?(' \
              r'INTERNAL\s+|EDITIONABLE\s+|NONEDITIONABLE\s+|CONSTRAINT\s+|TEMPORARY\s+|TEMP\s+|PUBLIC\s+)?(' \
              r'RECURSIVE\s+)?(FORCE\s+)?(' \
              r'TABLE|FUNCTION|INDEX|VIEW|TRIGGER|ACCESS ' \
              r'METHOD|AGGREGATE|CAST|COLLATION|CONTEXT|CONVERSION|DATABASE|DATABASE LINK|DIRECTORY|DOMAIN|EVENT ' \
              r'TRIGGER|EXTENSION|FOREIGN DATA WRAPPER|FOREIGN TABLE|TEXT SEARCH CONFIGURATION|TEXT SEARCH ' \
              r'DICTIONARY|TEXT SEARCH PARSER|TEXT SEARCH TEMPLATE|GROUP|LANGUAGE|MATERIALIZED VIEW|OPERATOR ' \
              r'CLASS|OPERATOR FAMILY|OPERATOR|PACKAGE BODY|PACKAGE|POLICY|PROCEDURE|PUBLICATION|RESOURCE ' \
              r'GROUP|ROLE|RULE|SCHEMA|SEQUENCE|SERVER|STATISTICS|SUBSCRIPTION|SYNONYM|TABLESPACE|TRANSFORM ' \
              r'FOR|TYPE|USER)\s+(BODY\s+|MAPPING\s+|[ schema . ]\s+)?(IF NOT EXISTS\s+)?(\w+)\b'
    pattern2 = r"\bDECLARE\s+(\w+)\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    match = re.findall(pattern2, text, flags=re.IGNORECASE)
    if match:
        for i in range(len(match)):
            matches.append(match[i])
    return matches


def extract_else_dml_statements(text):
    name = []
    pattern1 = r'\bALTER\s+(' \
               r'TABLE|FUNCTION|INDEX|VIEW|TRIGGER|ACCESS ' \
               r'METHOD|AGGREGATE|CAST|COLLATION|CONTEXT|CONVERSION|DATABASE|DATABASE LINK|DIRECTORY|DOMAIN|EVENT ' \
               r'TRIGGER|EXTENSION|FOREIGN DATA WRAPPER|FOREIGN TABLE|TEXT SEARCH CONFIGURATION|TEXT SEARCH ' \
               r'DICTIONARY|TEXT SEARCH PARSER|TEXT SEARCH TEMPLATE|GROUP|LANGUAGE|MATERIALIZED VIEW|OPERATOR ' \
               r'CLASS|OPERATOR FAMILY|OPERATOR|PACKAGE BODY|PACKAGE|POLICY|PROCEDURE|PUBLICATION|RESOURCE ' \
               r'GROUP|ROLE|RULE|SCHEMA|SEQUENCE|SERVER|STATISTICS|SUBSCRIPTION|SYNONYM|TABLESPACE|TRANSFORM ' \
               r'FOR|TYPE|USER)\s+(BODY\s+|MAPPING\s+)?(IF EXISTS\s+)?(\w+)\b'
    pattern2 = r'\bCLUSTER\s+(\w+)\b|\bCALL/EXEC\s+(\w+)\b|\bCALL\s+(\w+)\b|\bANALYZE\s+(\w+)\b|\bDELETE\s+FROM\s+(' \
               r'ONLY\b)(\w+)\b'
    pattern3 = r'\bCOMMENT ON\s+(TABLE|FUNCTION|INDEX|VIEW|TRIGGER|ACCESS ' \
               r'METHOD|AGGREGATE|CAST|COLLATION|CONTEXT|CONVERSION|DATABASE|DATABASE LINK|DIRECTORY|DOMAIN|EVENT ' \
               r'TRIGGER|EXTENSION|FOREIGN DATA WRAPPER|FOREIGN TABLE|TEXT SEARCH CONFIGURATION|TEXT SEARCH ' \
               r'DICTIONARY|TEXT SEARCH PARSER|TEXT SEARCH TEMPLATE|GROUP|LANGUAGE|MATERIALIZED VIEW|OPERATOR ' \
               r'CLASS|OPERATOR FAMILY|OPERATOR|PACKAGE BODY|PACKAGE|POLICY|PROCEDURE|PUBLICATION|RESOURCE ' \
               r'GROUP|ROLE|RULE|SCHEMA|SEQUENCE|SERVER|STATISTICS|SUBSCRIPTION|SYNONYM|TABLESPACE|TRANSFORM ' \
               r'FOR|TYPE|USER)\s+(IF EXISTS\s+)?(\w+)\b'
    pattern4 = r'\bDELETE\s+(PROCEDURAL\s+|PUBLIC\s+)?(TABLE|FUNCTION|INDEX|VIEW|TRIGGER|ACCESS ' \
               r'METHOD|AGGREGATE|CAST|COLLATION|CONTEXT|CONVERSION|DATABASE|DATABASE LINK|DIRECTORY|DOMAIN|EVENT ' \
               r'TRIGGER|EXTENSION|FOREIGN DATA WRAPPER|OWNED BY|FOREIGN TABLE|TEXT SEARCH CONFIGURATION|TEXT SEARCH ' \
               r'DICTIONARY|TEXT SEARCH PARSER|TEXT SEARCH TEMPLATE|GROUP|LANGUAGE|MATERIALIZED VIEW|OPERATOR ' \
               r'CLASS|OPERATOR FAMILY|OPERATOR|PACKAGE BODY|PACKAGE|POLICY|PROCEDURE|PUBLICATION|RESOURCE ' \
               r'GROUP|ROLE|RULE|SCHEMA|SEQUENCE|SERVER|STATISTICS|SUBSCRIPTION|SYNONYM|TABLESPACE|TRANSFORM ' \
               r'FOR|TYPE|USER)\s+(CONCURRENTLY\s+|BODY\s+|MAPPING\s+)?(IF EXISTS\s+)?(\w+)\b'
    pattern5 = r'\bINSERT\s+(ALL\s+)?INTO\s+(\w+)\b|\bLOCK TABLE\s+(\w+)\b|\bUPDATE\s+(ONLY\s+)?(\w+)\b|' \
               r'SELECT\s+(.*)\s+FROM\s+(\w+)'
    match1 = re.findall(pattern1, text, flags=re.IGNORECASE)
    match2 = re.findall(pattern2, text, flags=re.IGNORECASE)
    match3 = re.findall(pattern3, text, flags=re.IGNORECASE)
    match4 = re.findall(pattern4, text, flags=re.IGNORECASE)
    match5 = re.findall(pattern5, text, flags=re.IGNORECASE)
    match = []
    if match1:
        for i in range(len(match1)):
            name.append(match1[i][len(match1) - 1])
    if match2:
        for i in range(len(match2)):
            name.append(match2[i][len(match2) - 1])
    if match3:
        for i in range(len(match3)):
            name.append(match3[i][len(match3) - 1])
    if match4:
        for i in range(len(match4)):
            name.append(match4[i][len(match4) - 1])
    if match5:
        for i in range(len(match5)):
            name.append(match5[i][len(match5) - 1])
    return name


def extract_table_name(sql):
    table = sql_metadata.get_query_tables(sql)
    alias = sql_metadata.get_query_table_aliases(sql)
    return table, alias


def pad_name(text):
    sqls = split_sqls(text)
    flag = 0  # 是否出现未记录的表，出现错误，终止这个训练例子
    for i in range(len(sqls)):
        print(sqls[i])
        if sqls[i].startswith("\\set SQLTERM "):
            print("m")
            continue
        match = extract_create_statements(sqls[i])
        name = []
        if not match:
            continue
        for x in range(len(match)):
            name.append(match[x][len(match[x]) - 1])
        mm = extract_else_dml_statements(sqls[i])
        if mm:
            for y in range(len(mm)):
                name.append(mm[y][len(mm[y]) - 1])
        for j in range(len(name)):
            if name[j] in createSQL.keys():
                print(name[j])
                if createSQL.get(name[j]) in text:
                    continue
                else:
                    text = text + createSQL.get(name[j])
            else:
                text = ""
                flag = 1
                break
        if flag == 1:
            break
    return text


def pre(path):
    files = []
    filename = './tests/'
    idx = 0
    idx1 = 0
    for root, d_names, f_names in os.walk(path):
        for f in f_names:
            files.append(os.path.join(root, f))
    files = sorted(files)
    for file in files:
        if not file.endswith('.txt'):
            continue
        text = open(file, 'r', encoding='utf-8').read()
        text = remove_comments(text)
        text = remove_error_and_detail(text)
        collect_create_sql(text)
        if text == "":
            continue
        else:
            ff = filename + str(idx) + '.txt'
            idx = idx + 1
            f = open(ff, 'w')
            f.write(text)
    # for file in files:
    #     if not file.endswith('.txt'):
    #         continue
    #     text = open(file, 'r', encoding='utf-8').read()
    #     print(text)
    #     collect_create_sql(text)
    #     text = clean(text)
    #     ff = filename + str(idx) + '.txt'
    #     idx = idx + 1
    #     f = open(ff, 'w')
    #     f.write(text)



sql = open('./a.txt', 'r', encoding='utf-8').read()
t = split_sqls(sql)
print(t)
# path = r"/Users/weirdozwhy/Desktop/testcase"
# pre(path)

# # 正则表达式模式，匹配括号内的内容
# pattern = r"\((.*?)\);"
# match = re.search(pattern, create_table_sql)
#
# # 如果匹配成功
# if match:
#     # 获取括号内的内容
#     column_str = match.group(1)
#     # 将内容按逗号拆分成单个列
#     columns = column_str.split(",")
#     # 去除列名前后的空格，并输出
#     for column in columns:
#         print(column.strip())


# sql = '   select x1,x2 from liepin.a as atable left         join b on atable.id = b.id right join c on c.id = atable.id'
# sql = ' '.join(sql.split())
#
# print(sql_metadata.get_query_tables("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');"))
# print(sql_metadata.get_query_tables("select x1, x2 from (select x1, x2 from (select x1, x2 from apple.a)) left join orange.b as ob on a.id=ob.id   where b.id in (select id from f)"))
# print(sql_metadata.get_query_tables("select * from user as u where u.id = 99"))
#
# print(sql_metadata.get_query_tables("UPDATE accounts SET contact_first_name = first_name, contact_last_name = last_name FROM salesmen WHERE salesmen.id = accounts.sales_id;"))
