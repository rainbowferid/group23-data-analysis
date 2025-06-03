import pandas as pd
import sqlite3
from flask import Flask, jsonify, request, render_template
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

from flask_cors import CORS

app = Flask(__name__)
DATABASE = 'bilibili.db'
CORS(app)  # 允许跨域请求

# 连接数据库
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 首页
@app.route('/')
def index():
    return render_template('index.html')


# 获取视频列表
@app.route('/api/videos', methods=['GET'])
def get_videos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')

    conn = get_db_connection()

    # 构建查询
    query = "SELECT * FROM rank_all"
    params = []

    if search:
        query += " WHERE 视频名称 LIKE ? OR UP主 LIKE ?"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    videos = conn.execute(query, params).fetchall()

    # 获取总数
    count_query = "SELECT COUNT(*) FROM rank_all"
    if search:
        count_query += " WHERE 视频名称 LIKE ? OR UP主 LIKE ?"
    total = conn.execute(count_query, params[:-2]).fetchone()[0]

    conn.close()

    return jsonify({
        'videos': [dict(video) for video in videos],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })


# 获取统计信息
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()

    # 总视频数
    total_videos = conn.execute("SELECT COUNT(*) FROM rank_all").fetchone()[0]

    # 总播放量
    total_views = conn.execute(
        "SELECT SUM(CAST(REPLACE(REPLACE(播放量, '万', '0000'), '亿', '00000000') AS INTEGER)) FROM rank_all").fetchone()[
        0]

    # 总点赞量
    total_likes = conn.execute(
        "SELECT SUM(CAST(REPLACE(REPLACE(点赞量, '万', '0000'), '亿', '00000000') AS INTEGER)) FROM rank_all").fetchone()[
        0]

    # 平均播放量最高的UP主
    top_ups = conn.execute("""
        SELECT UP主, AVG(CAST(REPLACE(REPLACE(播放量, '万', '0000'), '亿', '00000000') AS INTEGER)) as avg_views
        FROM rank_all
        GROUP BY UP主
        ORDER BY avg_views DESC
        LIMIT 5
    """).fetchall()

    # 视频发布时间分布
    time_distribution = conn.execute("""
        SELECT STRFTIME('%H', 发布时间) as hour, COUNT(*) as count
        FROM rank_all
        WHERE 发布时间 LIKE '20__-__-__ __:__:__'
        GROUP BY hour
        ORDER BY hour
    """).fetchall()

    conn.close()

    return jsonify({
        'total_videos': total_videos,
        'total_views': total_views,
        'total_likes': total_likes,
        'top_ups': [{'up': up['UP主'], 'avg_views': int(up['avg_views'])} for up in top_ups],
        'time_distribution': [{'hour': td['hour'], 'count': td['count']} for td in time_distribution]
    })


# 获取播放量和互动数据
@app.route('/api/engagement', methods=['GET'])
def get_engagement():
    conn = get_db_connection()

    # 获取播放量、点赞量、评论量等数据
    data = conn.execute("""
        SELECT 
            视频名称,
            CAST(REPLACE(REPLACE(播放量, '万', '0000'), '亿', '00000000') AS INTEGER) as views,
            CAST(REPLACE(REPLACE(点赞量, '万', '0000'), '亿', '00000000') AS INTEGER) as likes,
            CAST(REPLACE(REPLACE(硬币量, '万', '0000'), '亿', '00000000') AS INTEGER) as coins,
            CAST(REPLACE(REPLACE(收藏量, '万', '0000'), '亿', '00000000') AS INTEGER) as favorites,
            CAST(REPLACE(REPLACE(弹幕量, '万', '0000'), '亿', '00000000') AS INTEGER) as danmaku
        FROM rank_all
        WHERE 播放量 NOT LIKE '%-%' AND 点赞量 NOT LIKE '%-%'
        ORDER BY views DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    return jsonify([dict(item) for item in data])


# 获取标签云数据
@app.route('/api/tags', methods=['GET'])
def get_tags():
    conn = get_db_connection()

    # 获取所有标签
    tags_data = conn.execute("SELECT 标签 FROM rank_all").fetchall()

    # 处理标签数据
    tag_counts = {}
    for row in tags_data:
        tags = row['标签'].split(',') if row['标签'] else []
        for tag in tags:
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 获取出现次数最多的50个标签
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:50]

    conn.close()

    return jsonify([{'name': tag, 'value': count} for tag, count in top_tags])


# 生成播放量分布图表
@app.route('/api/chart/views_distribution', methods=['GET'])
def get_views_distribution_chart():
    conn = get_db_connection()

    # 获取播放量数据
    views_data = conn.execute("""
        SELECT CAST(REPLACE(REPLACE(播放量, '万', '0000'), '亿', '00000000') AS INTEGER) as views
        FROM rank_all
        WHERE 播放量 NOT LIKE '%-%'
    """).fetchall()

    conn.close()

    # 转换为DataFrame
    df = pd.DataFrame([{'views': item['views']} for item in views_data])

    # 创建图表
    plt.figure(figsize=(10, 6))
    plt.hist(df['views'], bins=20, alpha=0.7, color='skyblue')
    plt.title('视频播放量分布')
    plt.xlabel('播放量')
    plt.ylabel('视频数量')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 转换为base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return jsonify({'image': f'data:image/png;base64,{plot_url}'})



if __name__ == '__main__':
    app.run(debug=True,port=5000)