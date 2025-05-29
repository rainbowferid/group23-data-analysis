import sqlite3
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os


def load_data(db_file, table_name="popular_history", column="标签"):
    """从SQLite数据库加载数据"""
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.execute(f"SELECT {column} FROM {table_name}")
            return [row[0] for row in cursor.fetchall() if row[0]]
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return []


def load_stopwords(file_path="stopwords.txt"):
    """加载停用词表"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f)
    return set()


def process_text(text_list, stopwords=None):
    """处理文本数据，包括分词和停用词过滤"""
    if stopwords is None:
        stopwords = set()

    all_text = ",".join(text_list)
    words = jieba.cut(all_text)
    filtered_words = [
        word for word in words
        if word.strip() and word not in stopwords
    ]
    return " ".join(filtered_words)


def preprocess_mask_image(image_path, output_path="processed_mask.png"):
    """将图片中非白色部分转换为黑色"""
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        return None

    try:
        # 打开图片并转换为RGB模式
        img = Image.open(image_path).convert("RGB")
        pixels = img.load()

        # 将非白色像素转换为黑色
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = pixels[i, j]
                # 判断是否为白色(或接近白色)
                if r < 240 or g < 240 or b < 240:
                    pixels[i, j] = (0, 0, 0)  # 设为黑色

        # 保存处理后的图片
        img.save(output_path)
        print(f"掩码图片已处理并保存至: {output_path}")

        # 转换为numpy数组供词云使用
        return np.array(img)
    except Exception as e:
        print(f"处理掩码图片时出错: {e}")
        return None


def generate_wordcloud(text, mask_array=None, font_path="simhei.ttf", output_path="wordcloud.png"):
    """生成并保存词云图"""
    # 配置词云参数
    wc = WordCloud(
        font_path=font_path,
        background_color="white",
        mask=mask_array,
        width=1000,
        height=600,
        max_words=200,
        max_font_size=100,
        random_state=42,
        contour_width=1,
        contour_color='steelblue'
    )

    wordcloud = wc.generate(text)
    wordcloud.to_file(output_path)
    print(f"词云图已保存至: {output_path}")

    # 显示词云图
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()


def main():
    # 配置参数
    DB_FILE = "bilibili.db"
    MASK_PATH = "cloud.jpg"
    OUTPUT_PATH = "bilibili_tags_wordcloud.png"
    FONT_PATH = "simhei.ttf"

    # 加载数据
    tags = load_data(DB_FILE)
    if not tags:
        print("未找到有效标签数据")
        return

    # 加载停用词（可选）
    stopwords = load_stopwords()

    # 处理文本
    processed_text = process_text(tags, stopwords)

    # 预处理掩码图片
    mask_array = preprocess_mask_image(MASK_PATH) if MASK_PATH else None

    # 生成词云
    generate_wordcloud(processed_text, mask_array, FONT_PATH, OUTPUT_PATH)


if __name__ == "__main__":
    main()