import sqlite3

def query_data():
    try:
        # 1. 连接到数据库文件
        # 请确保 db.sqlite3 在当前脚本运行的目录下，或者填写绝对路径
        conn = sqlite3.connect('D:/github_repo/智能产线综合应用实训/line/myproject/db.sqlite3') 
        cursor = conn.cursor()
        #获取历史该表的结构
        cursor.execute("PRAGMA table_info(myline_workinghistory)")
        print(cursor.fetchall())
        
        # 2. 执行查询 SQL
        # 获取最近插入的 5 条数据，按 ID 倒序排列
        #  二个表 一个设备名 myline_abbrobot  一个工作历史表 myline_workinghistory
        sql = "SELECT * FROM myline_abbrobot ORDER BY id DESC LIMIT 5"
        cursor.execute(sql)
        
        
        # 3. 获取所有结果
        rows = cursor.fetchall()
        #查看对应的键名
        print("key：",rows[0][0])

  

        # 4. 遍历并打印每一行
        for row in rows:
            # row 是一个元组，顺序对应表结构
            print(row)  # 打印每一行数据
            
            

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    query_data()
