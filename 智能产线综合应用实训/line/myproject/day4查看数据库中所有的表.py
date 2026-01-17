import sqlite3

# 数据库文件路径
db_path = 'D:/github_repo/智能产线综合应用实训/line/myproject/db.sqlite3'

try:
    # 1. 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. 执行查询系统表的 SQL 语句
    # type='table' 表示我们只查找表，不查找索引
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # 3. 获取所有结果
    tables = cursor.fetchall()

    print(f"数据库 '{db_path}' 中的所有表：")
    print("-" * 30)
    
    if tables:
        for table in tables:
            # fetchall 返回的是元组列表，例如 [('myapp_table1',), ('auth_user',)]
            # table[0] 就是表名
            print(f"表名: {table[0]}")
    else:
        print("该数据库中没有找到任何表。")

except sqlite3.Error as e:
    print(f"发生错误: {e}")
finally:
    # 4. 关闭连接
    if conn:
        conn.close()