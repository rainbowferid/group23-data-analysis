import pandas as pd
import sqlite3

# 读取 Excel 文件
excel_file = 'rank.xlsx'
df = pd.read_excel(excel_file)
# 连接到 SQLite 数据库
db_file = 'bilibili.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
# 创建表（如果不存在）
create_table_query = """
CREATE TABLE IF NOT EXISTS rank_all (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    视频名称 TEXT,
    视频链接 TEXT,
    UP主 TEXT,
    播放量 TEXT,
    点赞量 TEXT,
    硬币量 TEXT,
    收藏量 TEXT,
    弹幕量 TEXT,
    发布时间 TEXT,
    标签 TEXT
)
"""
cursor.execute(create_table_query)

for _, row in df.iterrows():
    insert_query = """
    INSERT INTO rank_all (
        视频名称, 视频链接, UP主, 播放量, 点赞量, 硬币量, 收藏量, 弹幕量, 发布时间, 标签
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, (
        row['视频名称'],
        row['视频链接'],
        row['UP主'],
        row.get('播放量', ''),
        row.get('点赞量', ''),
        row.get('硬币量', ''),
        row.get('收藏量', ''),
        row.get('弹幕量', ''),
        row.get('发布时间', ''),
        row.get('标签', '')
    ))
# 提交事务并关闭连接
conn.commit()
conn.close()

print(f"数据已成功导入 SQLite 数据库: {db_file}")