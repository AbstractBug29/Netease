import tkinter as tk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import jieba
import json
import random
from alive_progress import alive_bar
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pygame


class MusicAnalyzerUI:
    def __init__(self):
        #UI界面设计
        self.window = tk.Tk()
        self.window.title("简陋的网易云歌单分析工具")
        self.window.geometry("500x600")

        self.label = tk.Label(self.window, text="请输入你的ID：", font=("Arial", 14))
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.window, font=("Arial", 12))
        self.entry.pack()

        self.button = tk.Button(self.window, text="分析", command=self.analyze_music, font=("Arial", 12))
        self.button.pack(pady=10)

        self.result_text = tk.Text(self.window, height=10, width=50, font=("Arial", 12))
        self.result_text.pack()

        self.button1 = tk.Button(self.window, text="你的Top 100首歌曲",
                                 command=self.display_Top100_songs, font=("Arial", 12))
        self.button2 = tk.Button(self.window, text="推荐的20首歌曲", command=self.display_recommended_songs,
                                 font=("Arial", 12))

        self.button3 = tk.Button(self.window, text="你最常听的歌手", command=self.display_singer_listening_times,
                                 font=("Arial", 12))

        self.button4 = tk.Button(self.window, text="你的听歌类型", command=self.display_favorite_song_types,
                                 font=("Arial", 12))

        self.button5 = tk.Button(self.window, text="你的听歌标签", command=self.display_favorite_song_tags,
                                 font=("Arial", 12))

        self.button6 = tk.Button(self.window, text="评论区常见词汇", command=self.display_common_words,
                                 font=("Arial", 12))

        self.button7 = tk.Button(self.window, text="和你有相似口味的人", command=self.display_simi_people,
                                 font=("Arial", 12))

        self.button_exit = tk.Button(self.window, text="Exit", command=self.exit_program, font=("Arial", 12))
        self.button_exit.pack(side=tk.RIGHT, padx=10, pady=10)

        self.button_clear = tk.Button(self.window, text="Clear", command=self.clear_data, font=("Arial", 12))
        self.button_clear.pack(side=tk.LEFT, padx=10, pady=10)

        self.play_button = tk.Button(self.window, text="播放音乐", command=self.play_music, font=("Arial", 12))
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.window, text="暂停音乐", command=self.pause_music, font=("Arial", 12))
        self.pause_button.pack(side=tk.RIGHT)

        self.music_file = "music.mp3"
        self.paused = False

    def analyze_music(self):
        # 获取用户id，进行网页爬虫
        # 1602637656 自己的uid
        # 549373101 室友的uid
        user_id = self.entry.get()

        rank_url = f"https://music.163.com/user/songs/rank?id={user_id}"

        browser = webdriver.Chrome()

        browser.get(rank_url)

        browser.switch_to.frame('g_iframe')

        mouse_click = browser.find_element(By.ID, "songsall")
        mouse_click.click()

        browser.implicitly_wait(1)
        time.sleep(1)

        htmlrec = browser.page_source
        pagerec = BeautifulSoup(htmlrec, 'html.parser')

        pattern = re.compile(r'^/song\?id=\d+$')

        songs = pagerec.find(class_="g-wrap p-prf").find(class_="m-record").find(class_="j-flag").find_all("li")

        # 获取历史播放前一百的歌曲信息和id信息
        singers = []
        song_title = []
        singer_listening_times = {}
        song_id = []
        for song in songs:
            singer = song.find(class_="s-fc8").text.replace('\xa0', ' ').replace(' -', '')
            singers.append(singer)

        for titles in songs:
            title = titles.find('a', href=pattern).text
            song_title.append(title)

        self.song_intro = dict(zip(song_title, singers))

        for i in songs:
            song_id.append(i.find('a')['href'].replace('/song?id=', ''))

        # 获取歌手出现次数的排名
        flattened_singers = []
        for i in range(len(singers)):
            if '/' in singers[i]:
                singers[i] = singers[i].split('/')

        for item in singers:
            if isinstance(item, list):
                flattened_singers.extend(item)
            else:
                flattened_singers.append(item)

        for i in flattened_singers:
            singer_listening_times.setdefault(i, 0)
            singer_listening_times[i] += 1

        self.sorted_singer_listening_times = dict(
            sorted(singer_listening_times.items(), key=lambda x: x[1], reverse=True))

        # 获取推荐歌曲
        recommend_titles = []
        recommend_singers = []
        for i in range(7):
            recommend_song_url = f"http://localhost:3000/simi/song?id={song_id[i]}"
            page2 = requests.get(recommend_song_url)
            data2 = json.loads(page2.text)
            songs_data = data2['songs']
            for song in songs_data:
                recommend_titles.append(song['name'])
            for singer in songs_data:
                recommend_singers.append(singer['artists'][0]['name'])

        self.recommend_songs = dict(zip(recommend_titles, recommend_singers))

        # 我国省份信息
        Province_info = {"北京": 110000, "天津": 120000, "河北": 130000, "山西": 140000, "内蒙古": 150000,
                         "辽宁": 210000,
                         "吉林": 220000, "黑龙江": 230000, "上海": 310000, "江苏": 320000, "浙江": 330000,
                         "安徽": 340000,
                         "福建": 350000, "江西": 360000, "山东": 370000, "河南": 410000, "湖北": 420000, "湖南": 430000,
                         "广东": 440000, "广西": 450000, "海南": 460000, "四川": 510000, "贵州": 520000, "云南": 530000,
                         "西藏": 540000, "重庆": 500000, "陕西": 610000, "甘肃": 620000, "青海": 630000, "宁夏": 640000,
                         "新疆": 650000, "中国台湾": 830000, "中国香港": 810000, "中国澳门": 820000}

        # 获取播放量前10的歌曲里的热门评论以及热门评论用户的id
        simi_province = []
        simi_gender = []
        Hotcomments = []
        user_in_hotcomments = []
        for i in range(10):
            hotComments_url = f"http://localhost:3000/comment/hot?id={song_id[i]}&type=0&limit=30"
            page = requests.get(hotComments_url)
            data = json.loads(page.text)
            comments_data = data['hotComments']
            for comment in comments_data:
                Hotcomments.append(comment['content'])
            for userID in data['hotComments']:
                user_in_hotcomments.append(userID['user']['userId'])

        # 分析热门评论用户的信息
        with alive_bar(len(user_in_hotcomments), force_tty=True) as bar1:
            for user_id in user_in_hotcomments[0:50]:
                url = 'http://localhost:3000/user/detail?uid=' + str(user_id)
                r = requests.get(url)
                record = r.json()
                if record["code"] == 404:
                    continue
                place = record['profile']['province']
                gender = record['profile']['gender']
                try:
                    for i, j in Province_info.items():
                        if int(place) == j:
                            simi_province.append(i)
                        else:
                            simi_province.append("未知地区")
                        if gender == 1:
                            simi_gender.append("男生")
                        if gender == 2:
                            simi_gender.append("女生")
                except:
                    pass
                bar1()

        # 获取省份和性别信息，按出现次数排列
        dict_simi_province = {}
        dict_simi_gender = {}
        for i in simi_province:
            dict_simi_province.setdefault(i, 0)
            dict_simi_province[i] += 1
        for i in simi_gender:
            dict_simi_gender.setdefault(i, 0)
            dict_simi_gender[i] += 1

        # 排序
        self.sorted_simi_province = dict(sorted(dict_simi_province.items(), key=lambda x: x[1], reverse=True))
        self.sorted_simi_gender = dict(sorted(dict_simi_gender.items(), key=lambda x: x[1], reverse=True))

        # 获取歌曲的类型与其风格标签，按出现次数排序
        song_types = []
        song_tags = []
        favorite_types = {}
        favorite_tags = {}

        for i in range(0, 100):
            try:
                song_url = f"http://localhost:3000/song/wiki/summary?id={song_id[i]}"
                page = requests.get(song_url)
                data = json.loads(page.text)
                types_data = data['data']['blocks'][1]['creatives'][0]['resources']
                for i in types_data:
                    song_types.append(i['uiElement']['mainTitle']['title'])
                tags_data = data['data']['blocks'][1]['creatives'][1]['resources']
                for i in tags_data:
                    song_tags.append(i['uiElement']['mainTitle']['title'])
            except:
                continue

        for i in song_types:
            if '-' in i:
                song_divided = i.split('-')
                song_types.remove(i)
                song_types.append(song_divided[0])

        for i in song_types:
            favorite_types.setdefault(i, 0)
            favorite_types[i] += 1

        for i in song_tags:
            if '-' in i:
                song_divided = i.split('-')
                song_tags.remove(i)
                song_tags.append(song_divided[0])

        for i in song_tags:
            favorite_tags.setdefault(i, 0)
            favorite_tags[i] += 1

        sorted_favorite_type = dict(sorted(favorite_types.items(), key=lambda x: x[1], reverse=True))
        self.sorted_favorite_tags = dict(sorted(favorite_tags.items(), key=lambda x: x[1], reverse=True))
        self.sorted_favorite_types = {k: v for k, v in sorted_favorite_type.items() if '-' not in k}

        # 创建词云
        module_pic = path.dirname(__file__)
        mask = np.array(Image.open(path.join(module_pic, "music.png")))
        self.tag_pic = WordCloud(scale=1.5, font_path='/font/msyh.ttc', background_color='white',
                                 mask=mask).generate_from_frequencies(self.sorted_favorite_tags)
        self.type_pic = WordCloud(scale=1.5, font_path='/font/msyh.ttc', background_color='white',
                                  mask=mask).generate_from_frequencies(self.sorted_favorite_types)
        self.favorite_singer = WordCloud(scale=1.5, font_path='/font/msyh.ttc', background_color='white',
                                         mask=mask).generate_from_frequencies(self.sorted_singer_listening_times)

        # 用jieba库获取评论区关键词和出现次数多的词
        keyword_counts = {}
        self.common_words = []
        for comment in Hotcomments:
            words = jieba.lcut(comment)
            for word in words:
                if len(word) >= 2:
                    keyword_counts.setdefault(word, 0)
                    keyword_counts[word] += 1

        sorted_keywords = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))

        for word in sorted_keywords.keys():
            if word in self.sorted_favorite_tags.keys():
                self.common_words.append(word)

        if not self.common_words:
            random_tags = random.sample(self.sorted_favorite_tags.keys(), 3)
            self.common_words.extend(random_tags)

        browser.quit()

        self.button1.pack()
        self.button2.pack()
        self.button3.pack()
        self.button4.pack()
        self.button5.pack()
        self.button6.pack()
        self.button7.pack()

    def display_Top100_songs(self):
        result = "TOP 100 Favorite Songs:\n"
        for title, singer in self.song_intro.items():
            result += f"{title} - {singer}\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def display_singer_listening_times(self):
        result = "Your Favorite Singers:\n"
        for i, (singer, count) in enumerate(self.sorted_singer_listening_times.items()):
            if i >= 5:
                break
            result += f"{singer} - {count} times\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

        plt.imshow(self.favorite_singer)
        plt.axis('off')
        plt.show()

    def display_recommended_songs(self):
        result = "20 songs that you may like:\n"
        for i, (song, singer) in enumerate(self.recommend_songs.items()):
            if i >= 20:
                break
            result += f"{song} - {singer}\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def display_favorite_song_types(self):
        result = "TOP 5 Your Song Types:\n"
        for i, (type, count) in enumerate(self.sorted_favorite_types.items()):
            if i >= 5:
                break
            result += f"'{type}' appears {count} times\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

        plt.imshow(self.type_pic)
        plt.axis('off')
        plt.show()

    def display_favorite_song_tags(self):
        result = "TOP 5 Your Song Tags:\n"
        for i, (tag, count) in enumerate(self.sorted_favorite_tags.items()):
            if i >= 5:
                break
            result += f"{tag} appears {count} times\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

        plt.imshow(self.tag_pic)
        plt.axis('off')
        plt.show()

    def display_common_words(self):
        result = "Common words in comments:\n"
        for i in self.common_words:
            result += f"{i}\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def display_simi_people(self):
        result = "Inforamtion about people with similar favors:\n"
        result += "\nWho are they:\n"
        for i, j in self.sorted_simi_gender.items():
            result += f"{i} - {j}人\n"
        result += "\nWhere are they:\n"
        for i, j in self.sorted_simi_province.items():
            result += f"{i} - {j}人\n"
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def exit_program(self):
        self.window.destroy()

    def clear_data(self):
        self.entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def play_music(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play()

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    analyzer_ui = MusicAnalyzerUI()
    analyzer_ui.run()
