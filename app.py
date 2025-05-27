from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)


@app.route('/rankList')
def get_rank_list():
    try:
        # 获取分页参数，默认为第1页
        page = request.args.get('page', 1, type=int)
        if page < 1:
            page = 1

        # 每页10条记录
        limit = 10
        offset = (page - 1) * limit

        # 检查数据库文件是否存在
        if not os.path.exists('bilibili.db'):
            return jsonify({"error": "数据库文件不存在"}), 404

        # 连接数据库
        conn = sqlite3.connect('bilibili.db')
        cursor = conn.cursor()

        # 查询总记录数
        cursor.execute("SELECT COUNT(*) FROM rank_all")
        total_count = cursor.fetchone()[0]

        # 查询当前页数据
        cursor.execute("SELECT 视频名称,UP主,发布时间,播放量,点赞量,视频链接 FROM rank_all LIMIT ? OFFSET ?", (limit, offset))
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # 计算总页数
        total_pages = (total_count + limit - 1) // limit

        # 关闭数据库连接
        conn.close()

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

    except sqlite3.Error as e:
        return jsonify({"error": f"数据库错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)