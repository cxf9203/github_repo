import sqlite3

def query_data():
    try:
        # 1. 连接到数据库文件
        # 请确保 db.sqlite3 在当前脚本运行的目录下，或者填写绝对路径
        conn = sqlite3.connect('D:/github_repo/智能产线综合应用实训/line/myproject/db.sqlite3') 
        cursor = conn.cursor()

        # 2. 执行查询 SQL
        # 获取最近插入的 5 条数据，按 ID 倒序排列
        sql = "SELECT * FROM robor_vision ORDER BY id DESC LIMIT 5"
        cursor.execute(sql)

        # 3. 获取所有结果
        rows = cursor.fetchall()

        print(f"找到 {len(rows)} 条记录:")
        print("-" * 60)
        # 打印表头
        print(f"{'ID':<5} {'检测数量':<8} {'OK数量':<8} {'合格率':<10} {'颜色':<10} {'形状':<10}")
        print("-" * 60)

        # 4. 遍历并打印每一行
        for row in rows:
            # row 是一个元组，顺序对应表结构
            # row[0]=id, row[1]=检测数量, row[2]=ok数量, row[3]=合格率, row[4]=颜色, row[5]=形状
            print(f"{row[0]:<5} {row[1]:<8} {row[2]:<8} {row[3]:<10.2%} {row[4]:<10} {row[5]:<10}")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    query_data()
