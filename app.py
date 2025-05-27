from flask import Flask, jsonify, request
import sqlite3
import os
from functools import wraps
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# 数据库文件路径
DB_PATH = 'bilibili.db'


# 数据库连接装饰器
def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not os.path.exists(DB_PATH):
            return jsonify({"error": "数据库文件不存在"}), 404

        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row  # 使用字典形式返回结果
                return func(conn, *args, **kwargs)
        except sqlite3.Error as e:
            return jsonify({"error": f"数据库错误: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"服务器错误: {str(e)}"}), 500

    return wrapper


@app.route('/rankList')
def get_rank_list():
    try:
        # 获取分页参数，默认为第1页
        page = max(1, request.args.get('page', 1, type=int))
        limit = 10
        offset = (page - 1) * limit

        @with_db_connection
        def query_data(conn):
            cursor = conn.cursor()

            # 查询总记录数
            cursor.execute("SELECT COUNT(*) FROM rank_all")
            total_count = cursor.fetchone()[0]

            # 查询当前页数据
            cursor.execute(
                """SELECT 视频名称,UP主,发布时间,播放量,点赞量,视频链接 
                   FROM rank_all LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            data = [dict(row) for row in cursor.fetchall()]

            return data, total_count

        data, total_count = query_data()

        # 计算总页数
        total_pages = max(1, (total_count + limit - 1) // limit)

        # 构建分页信息
        pagination = {
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
            "total_count": total_count,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }

        return jsonify({
            "data": data,
            "pagination": pagination
        })

    except Exception as e:
        return jsonify({"error": f"获取排行榜数据失败: {str(e)}"}), 500


@app.route('/playLoad')
@with_db_connection
def get_playload_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT 播放量, 弹幕量, 视频名称 FROM rank_all")
    data = [dict(row) for row in cursor.fetchall()]

    return jsonify({
        "data": data,
        "xAxis": "播放量",
        "yAxis": "弹幕量",
        "tooltip": ["视频名称", "播放量", "弹幕量"]
    })


@app.route('/playLike')
@with_db_connection
def get_playlike_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT 播放量, 点赞量, 收藏量, 视频名称 FROM rank_all")
    data = []

    for row in cursor.fetchall():
        item = dict(row)

        # 处理点赞量字段
        likes = item['点赞量']
        if likes.endswith('万'):
            item['点赞量'] = int(float(likes[:-1]) * 10000)
        else:
            item['点赞量'] = int(likes)

        # 处理收藏量字段（逻辑与点赞量相同）
        favorites = item['收藏量']
        if favorites.endswith('万'):
            item['收藏量'] = int(float(favorites[:-1]) * 10000)
        else:
            item['收藏量'] = int(favorites)

        data.append(item)

    return jsonify({
        "data": data,
        "xAxis": "播放量",
        "yAxis": "点赞量",
        "bubbleSize": "收藏量",
        "tooltip": ["视频名称", "播放量", "点赞量", "收藏量"]
    })


if __name__ == '__main__':
    app.run(debug=True,port=5000)