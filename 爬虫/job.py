from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd

url = 'https://www.bilibili.com/v/popular/rank/all'

# 创建一个空的 DataFrame 用于存储数据
data = {
    '视频名称': [],
    '视频链接': [],
    'UP主': [],
    '播放量': [],
    '点赞量': [],
    '硬币量': [],
    '收藏量': [],
    '弹幕量': [],
    '发布时间': [],
    '标签': [],

}

df = pd.DataFrame(data)
cnt = 0
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True, slow_mo=100)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url, timeout=5000)
    page.wait_for_load_state('networkidle')
    blog = page.content()
    info = BeautifulSoup(blog, 'html.parser')
    select = info.select(
        '#app > div > div.rank-container > div.rank-list-wrap > ul > li > div > div.info')



    for video in select:
        video_name = video.find(class_='title').text
        video_url = video.find(class_='title')['href'].split('//')[-1]
        up_name = video.find(class_='up-name').text.lstrip()
        play_count = video.find(class_='detail-state').text.split()[0]
        like_count = video.find(class_='detail-state').text.split()[1]

        print(f"视频名称: {video_name}")
        print(f"视频链接: {video_url}")
        print(f"UP主: {up_name}")
        print(f"播放量: {play_count}")
        print(f"弹幕量: {like_count}")

        page.goto('https://' + video_url, timeout=20000)
        page.wait_for_load_state('domcontentloaded')

        blog = page.content()
        info = BeautifulSoup(blog, 'html.parser')


        pub_date = info.find(class_='pubdate-ip-text')
        if pub_date == None:
            pub_date = info.find(class_='pubdate-count')

        pub_date = pub_date.text
        print(f"发布时间: {pub_date}")

        likes = info.find(class_='video-like-info')
        if (likes != None):
            likes = likes.text

        coins = info.find(class_='video-coin-info')
        if (coins != None):
            coins = coins.text

        fav = info.find(class_='video-fav-info')
        if (fav != None):
            fav = fav.text

        print(info)
        # duration = info.find(class_='bpx-player-ctrl-time-duration').text
        # print(duration)

        tags = [tag.text for tag in info.find_all(class_='tag-link')]
        tags_text = ', '.join(tags)
        print(f"标签: {tags_text}")
        print("-" * 50)

        # 将数据添加到 DataFrame
        new_row = {
            '视频名称': video_name,
            '视频链接': 'https://' + video_url,
            'UP主': up_name,
            '播放量': play_count,
            '点赞量': likes,
            '硬币量': coins,
            '收藏量': fav,
            '弹幕量': like_count,
            '发布时间': pub_date,
            '标签': tags_text,

        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # 只爬取一个视频用于测试
        break

    page.close()

# 将 DataFrame 保存为 Excel 文件
excel_file = 'bilibili_videos_all.xlsx'
df.to_excel(excel_file, index=False, engine='openpyxl')
print(f"数据已成功保存到 {excel_file}")