# -*- coding: utf-8 -*-
import re
import time
import requests
import json
import random
import matplotlib.pyplot as plt
import binascii
import clueai
import threading
import queue
import pprint
import pandas as pd
import numpy as np
from lxml import etree
from xpinyin import Pinyin
from lxml import etree

import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message
from botpy.types.message import Ark, ArkKv
from botpy.types.message import Embed, EmbedField
from collections import OrderedDict
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
columns = ['区服',"ID", "等级", "经验比", "战力GS", "击杀",'阵亡','KD','获得水晶数','获得金箱子','本周战斗水晶排名','本周战斗水晶数量','本周效率排名','本周效率','本周金水晶排名','本周金水晶数量','本周经验排名','本周经验','道具使用总量','道具使用详情','核能', '维修工具', '护甲提升', '伤害提升', '速度提升', '地雷', '金箱子', 'Grenade','战斗经验','战斗时间(小时)','time','原ID']
df_1 = pd.DataFrame(columns=columns)

# 将空的 DataFrame 写入 CSV 文件
df_1.to_csv('player_data.csv', mode="a",index=False)

columns_online=['时间','服务器','状态','战斗中','国服在线','4399在线']
df_online=pd.DataFrame(columns=columns_online)
'''df_online.to_csv('onlinedata.csv',  mode='a', index=False)'''

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
        await self.get_online_data()

    async def get_online_data(self):
        i = 0
        while True:
            i += 1
            current_timestamp = int(time.time())
            current_time = time.localtime(current_timestamp)
            next_hour_timestamp = current_timestamp - (current_time.tm_sec) + 600
            # print(current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec)
            wait_time = next_hour_timestamp - current_timestamp
            await asyncio.sleep(wait_time)
            rnd = str(int(random.randrange(10000, 99999)))
            url_online = "https://3dtank.com/s/status.js?rnd=" + rnd
            try:

                response_online = requests.get(url=url_online)
                json_data_online = json.loads(response_online.text)

                # pprint.pprint(json_data_online)
                inbattles = 0
                online = 0
                online_49 = 0
                server_host = ""
                for server in json_data_online["nodes"]:
                    server_host_a = json_data_online['nodes'][server]['endpoint']['host']
                    server_status = json_data_online['nodes'][server]['endpoint']['status']
                    inbattles_a = json_data_online["nodes"][server]["inbattles"]
                    online_a = json_data_online["nodes"][server]["online"]
                    online_49_a = json_data_online["nodes"][server]["partners"]["my_4399_com"]
                    inbattles += inbattles_a
                    online += online_a
                    online_49 += online_49_a
                    server_host += server_host_a

            except Exception:
                print('online_error')
                continue

            data = [next_hour_timestamp, server_host, server_status, inbattles, online, online_49]
            df_online = pd.DataFrame([data], columns=columns_online)
            print(i)

            df_online.to_csv('onlinedata.csv', header=False, mode='a', index=False)
        '''await self.schedule_message()

    async def schedule_message(self):
        channel_id = 543637697
        while True:
            current_timestamp = int(time.time())
            current_time = time.localtime(current_timestamp)
            next_hour_timestamp = current_timestamp - (current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec) + 86400
            wait_time = next_hour_timestamp - current_timestamp
            await asyncio.sleep(wait_time)
            embed = Embed(
                title="新年快乐",
                prompt="新年快乐",
                thumbnail={
                    "url": "https://en.tankiwiki.com/images/en/f/f6/Trophy_Augment_Shaft.png"
                },
                fields=[
                    EmbedField(name="1"),
                    EmbedField(name="1"),
                ],
            )
            await self.api.post_message(channel_id=channel_id, embed=embed)'''
    async def on_at_message_create(self, message: Message):
        _log.info(message.author.avatar)
        if "sleep" in message.content:
            await asyncio.sleep(20)
        _log.info(message.author.username)
        #print(message.content)
        #print(len(message.content))
        try:
            times_1=time.time()
            if message.content[0:29]=="<@!15425887405726406995> /国服 ":
                names=message.content[29:]
                url = 'https://ratings.3dtank.com/get_stat/profile/?user=' + names + '&lang=cn'
            elif message.content[0:29] == "<@!15425887405726406995> /外服 ":
                names = message.content[29:]
                url = "https://ratings.tankionline.com/api/eu/profile/?user=" + names + "&lang=cn"

            if message.content[0:29]=="<@!15425887405726406995> /国服 " or message.content[0:29] == "<@!15425887405726406995> /外服 ":
                start_time = time.time()
                names = message.content[29:]
                result_queue = queue.Queue()
                def get_json(url,names):
                    header = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
                    response = requests.get(url=url, headers=header)
                    # json_data_ra=json.dumps(response.text)
                    json_data = json.loads(response.text)
                    return json_data

                json_data = get_json(url,names)

                def get_basic_data(json_data, result_queue):  # 此部分为简单的索引语句
                    name = re.sub(r"\.","。",json_data['response']['name'])

                    if json_data["response"]["hasPremium"] == True:
                        name = "[VIP] " + name
                    rank = json_data['response']['rank']
                    rank_true = rank - 1
                    to_rank_list = ['新兵', '二等兵', '一等兵', '下士', '中士', '上士',
                                    '三级军士长', '二级军士长', '一级军士长', '军士长',
                                    '五级准尉',
                                    '四级准尉', '三级准尉', '二级准尉', '一级准尉',
                                    '特级准尉', '少尉', '中尉', '上尉', '少校',
                                    '中校', '上校', '准将', '少将', '中将',
                                    '上将', '元帅', '陆军元帅', '统帅', '大元帅']

                    if rank_true <= 29:
                        rank_name = to_rank_list[rank_true]

                    else:
                        rank_name = "传奇" + str(rank_true - 29)

                    score = json_data['response']['score']
                    score_base = json_data['response']['scoreBase']
                    score_next = json_data['response']['scoreNext']
                    score_0n = str(score) + '/' + str(score_next)
                    gearscore = json_data['response']['gearScore']
                    kills = json_data['response']['kills']
                    deaths = json_data['response']['deaths']
                    if deaths != 0:
                        k_d = kills / deaths
                    else:
                        k_d = kills

                    earnedCrystals = json_data['response']['earnedCrystals']
                    caughtGolds = json_data['response']['caughtGolds']
                    battle_crystals_position = json_data["response"]["rating"]["crystals"]["position"]
                    battle_crystals_value = json_data["response"]["rating"]["crystals"]["value"]
                    battle_efficiency_position = json_data["response"]["rating"]["efficiency"]["position"]
                    battle_efficiency_value = json_data["response"]["rating"]["efficiency"]["value"]
                    battle_golds_position = json_data["response"]["rating"]["golds"]["position"]
                    battle_golds_value = json_data["response"]["rating"]["golds"]["value"]
                    battle_score_position = json_data["response"]["rating"]["score"]["position"]
                    battle_score_value = json_data["response"]["rating"]["score"]["value"]

                    basic_data = 'ID:'+name + '\n' + '等级:' + rank_name + '\n' + '经验比:' + score_0n + '\n' + '战力GS:' + str( \
                        gearscore) + '\n' + '击杀:' + str( \
                        kills) + '\n' + '阵亡:' + str(deaths) + '\n' + 'KD:' + str(k_d) + '\n' + '获得水晶数:' + str( \
                        earnedCrystals) + '\n' + '获得金箱子:' + str(caughtGolds) + '\n' + "\t本周战斗水晶排名:" + str( \
                        battle_crystals_position) + '\n' + "\t本周战斗水晶数量:" + str( \
                        battle_crystals_value) + '\n' + '\t本周效率排名:' + str( \
                        battle_efficiency_position) + '\n' + '\t本周效率:' + str( \
                        battle_efficiency_value) + '\n' + '\t本周金水晶排名:' + str( \
                        battle_golds_position) + '\n' + '\t本周金水晶数量:' + str( \
                        battle_golds_value) + '\n' + '\t本周经验排名:' + str( \
                        battle_score_position) + '\n' + '\t本周经验:' + str( \
                        battle_score_value)
                    result_queue.put(basic_data)

                def get_supplies_data(json_data, result_queue):  # 此函数用于获取道具使用情况
                    sum_1 = 0
                    supplies_string = ""
                    for i in range(len(json_data['response']['suppliesUsage'])):
                        supplies_element_usage = json_data['response']['suppliesUsage'][i]['usages']
                        supplies_element_name = json_data['response']['suppliesUsage'][i]['name']
                        if i < 7:
                            n_u = '\t' + supplies_element_name + ":" + str(supplies_element_usage) + '\n'
                        else:
                            n_u = '\t' + supplies_element_name + ":" + str(supplies_element_usage)
                        supplies_string += n_u
                        sum_1 += supplies_element_usage

                    supplies_data = "\n" + "道具使用总量:" + str(
                        sum_1) + '\n' + "道具使用详情:" + "\n" + supplies_string
                    result_queue.put(supplies_data)

                def get_sum_data(json_data, result_queue):
                    sum_score = 0
                    sum_time = 0
                    for i in range(len(json_data['response']["modesPlayed"])):
                        score_mode = json_data['response']["modesPlayed"][i]["scoreEarned"]
                        sum_score += score_mode
                        time_mode = json_data['response']["modesPlayed"][i]["timePlayed"]
                        sum_time += time_mode
                    sum_data = "\n" + "战斗经验:" + str(sum_score) + "\n" + "匹配游戏时间(小时):" + str(
                        sum_time / 3600000)

                    result_queue.put(sum_data)

                def main(json_data):

                    thread_basic_data = threading.Thread(target=get_basic_data, name="thread_basic_data",
                                                         args=(json_data, result_queue))
                    thread_supplies_data = threading.Thread(target=get_supplies_data, name="thread_supplies_data",
                                                            args=(json_data, result_queue))
                    thread_sum_data = threading.Thread(target=get_sum_data, name="thread_sum_data",
                                                       args=(json_data, result_queue))

                    thread_basic_data.start()
                    thread_supplies_data.start()
                    thread_sum_data.start()
                    thread_sum_data.join()
                    thread_basic_data.join()
                    thread_supplies_data.join()

                    results = []
                    while not result_queue.empty():
                        result = result_queue.get()
                        results.append(result)

                    # 输出各个线程的返回值
                    user_data = " ".join(results)
                    end_time = time.time()
                    t = end_time - start_time
                    player_data = OrderedDict()
                    current_key = None

                    for line in ("区服:"+'国服'+'\n'+user_data + '\n' + 'time:' + str(times_1)+ '\n' +'原ID:'+names.lower()).strip().split('\n'):
                        if ':' in line:
                            current_key, value = line.split(':', 1)
                            player_data[current_key] = value.strip()
                        elif current_key == '道具使用详情':
                            # 处理道具使用详情部分，使用列表保存多个道具使用详情
                            current_key = current_key.strip()  # 移除前导空格
                            sub_key, sub_value = line.split(':', 1)
                            player_data.setdefault(current_key, []).append({sub_key.strip(): sub_value.strip()})

                    # 创建 DataFrame
                    df = pd.DataFrame([player_data])
                    columns_correct = ['区服',"ID", "等级", "经验比", "战力GS", "击杀", '阵亡', 'KD', '获得水晶数',
                                       '获得金箱子', '\t本周战斗水晶排名', '\t本周战斗水晶数量', '\t本周效率排名',
                                       '\t本周效率',
                                       '\t本周金水晶排名', '\t本周金水晶数量', '\t本周经验排名', '\t本周经验',
                                       '道具使用总量',
                                       '道具使用详情', '\t核能', '\t维修工具', '\t护甲提升', '\t伤害提升',
                                       '\t速度提升', '\t地雷', '\t金箱子', '\tGrenade', '战斗经验',
                                       '匹配游戏时间(小时)', 'time','原ID']
                    df = df[columns_correct]
                    # 保存 DataFrame 为 CSV 文件
                    df.to_csv('player_data.csv', header=False, mode='a', index=False)

                    return user_data + "\n" + "处理时间:" + str(t) + "秒"

                '''
                if names != "":
                    if json_data["responseType"] == "OK":
                        await message.reply(content=main(json_data))
                    else:
                        await message.reply(content="未查询到数据，可能开启隐藏数据或输入不正确")
                else:
                    await message.reply(content="请输入ID")
    
                '''
                if message.guild_id!="16488793382617768689":
                    if json_data["responseType"] == "OK":
                        await message.reply(content=main(json_data))
                    else:
                        await message.reply(content="未查询到数据，可能开启隐藏数据或输入不正确")
                else:
                    await message.reply(content="本频道无法使用该机器人，请加主频道1xsqbm99k4并联系频道主testanki")
                    await message.reply(file_image="JS.jpg")



        except Exception:
            await message.reply(content="机器人工作异常/网站连接异常/频道拦截消息")
        try:
            if message.content[0:31]=="<@!15425887405726406995> /人工智能 ":
                ai_msg=message.content[31:]
                cl = clueai.Client("gTEyLSh6lcDBMldhLcVN41100010100000", check_api_key=True)
                prompt = ai_msg
                prediction = cl.generate(model_name='ChatYuan-large', prompt=prompt)
                hex_data = prediction.generations[0].text
                await message.reply(content=hex_data)
        except Exception:
            print("ai对话失败")
        #except Exception:
        #    print("ai对话错误")
        try:
            if message.content[0:31] == "<@!15425887405726406995> /外服水晶榜":
                url = "https://ratings.tankionline.com/api/eu/top/"
                response_4 = requests.get(url=url)
                json_data_4 = json.loads(response_4.text)

                # list_crystals_ratings = []
                list_tanki_uid = []
                list_crystals_value = []
                sum_crystals_value = 0
                averange_crystals_value = 0
                for i in range(len(json_data_4["response"]["crystals"])):
                    tanki_uid = json_data_4["response"]["crystals"][i]["uid"]
                    crystals_value = json_data_4["response"]["crystals"][i]["value"]
                    list_tanki_uid.append(tanki_uid)
                    list_crystals_value.append(crystals_value)
                    sum_crystals_value = sum_crystals_value + crystals_value
                averange_crystals_value = sum_crystals_value / len(json_data_4["response"]["crystals"])
                plt.figure(figsize=(16, 12))
                plt.title("foregin service crystals list")
                plt.xlabel("nickname")
                plt.ylabel("amount")
                # plt.xticks(np.arange(1, len(collage_sort_drop_duplication) + 1),collage_sort_drop_duplication.to_numpy().tolist())
                plt.grid(ls=":", lw="1", color="blue")
                plt.axhline(averange_crystals_value, color="red", label="averange" + str(averange_crystals_value), lw=2)
                plt.plot(list_tanki_uid, list_crystals_value, color="k", label="crystals amount", lw=2)
                plt.legend()

                plt.savefig("waifushuijingbang.png")  # 可以从图表上直观获取到总平均分排名为前三的学院代码

                    #crystals_msg = str(tanki_uid) + "/" + str(crystals_value)
                    #list_crystals_ratings.append(crystals_msg)
            #print(list_crystals_ratings)
                #a="\n".join(list_crystals_ratings[0:10])

                url2 = "https://pages.tankionline.com/challenge-accepted"
                response = requests.get(url2)
                html = etree.HTML(response.text)
                # print(html.xpath("/html/body/div[4]/div[2]/div[2]/ul/li[4]/div[1]")[0].text)倒数第一级标签是每个账号的排名，ID，星数。倒数第二级标签是排名
                data_all = ""
                for i in range(1, 11):
                    position = html.xpath("/html/body/div[4]/div[2]/div[2]/ul/li[" + str(i) + "]/div[1]")[0].text
                    identy = html.xpath("/html/body/div[4]/div[2]/div[2]/ul/li[" + str(i) + "]/div[2]")[0].text
                    num = html.xpath("/html/body/div[4]/div[2]/div[2]/ul/li[" + str(i) + "]/div[3]")[0].text.replace(
                        " ", "")
                    data_per = str(position) + str(identy) + '  ' + str(num) + '\n'
                    data_all += data_per
                await message.reply(content="外服挑战排行榜前十玩家："+"\n"+data_all)
                await message.reply(file_image="waifushuijingbang.png")

                #await message.reply(content=list_tanki_uid[1:15])
        except Exception:
            print("外服水晶榜查询失败")

        try:
            if message.content[0:32]=="<@!15425887405726406995> /国服在线人数":

                #pprint.pprint(json_data_5)
                rnd = str(int(random.randrange(10000, 99999)))
                url_5 = "https://3dtank.com/s/status.js?rnd=" + rnd
                response_5 = requests.get(url=url_5)
                json_data_5 = json.loads(response_5.text)
                inbattles = 0
                online = 0
                online_49 = 0
                for server in json_data_5["nodes"]:
                    inbattles_a = json_data_5["nodes"][server]["inbattles"]
                    online_a = json_data_5["nodes"][server]["online"]
                    online_49_a = json_data_5["nodes"][server]["partners"]["my_4399_com"]
                    inbattles += inbattles_a
                    online += online_a
                    online_49 += online_49_a
                    
                rnd = str(int(random.randrange(10000, 99999)))
                url_5_test = "https://test.tankionline.com/public_test?v=" + rnd
                response_5_test = requests.get(url=url_5_test)

                json_data_test = json.loads(response_5_test.text)
                msg = ""

                for i in range(len(json_data_test)):
                    server = re.findall("deploy(.*?)-pubto", json_data_test[i]["Release"])
                    online_test_num = json_data_test[i]["UserCount"]
                    msg1 = "测试服" + str(server) + "区在线:"
                    msg += msg1 + str(online_test_num) + '\n'


                '''await message.reply(content="国服战斗人数"+str(inbattles)+"\n"+"国服在线人数"+str(online)+'\n'+"4399(3D坦克)在线人数"+str(online_49)+'\n'+msg)
'''
                if message.guild_id!="16488793382617768689":
                    await message.reply(content="国服战斗人数"+str(inbattles)+"\n"+"国服在线人数"+str(online)+'\n'+"4399(3D坦克)在线人数"+str(online_49)+'\n'+msg)
                else:
                    await message.reply(content="本频道无法使用该机器人，请加主频道1xsqbm99k4并联系频道主testanki")
                    await message.reply(file_image="JS.jpg")
        except Exception:
            await message.reply(content="失败，请重试")


        try:
            if message.content[0:31] == "<@!15425887405726406995> /国服水晶榜":
                url_6 = "https://ratings.3dtank.com/get_stat/top/"
                response = requests.get(url=url_6)
                response_json = json.loads(response.text)
                #print(response_json)

                sum_crystals_value_1 = 0
                list_crystals_uid_1 = []
                list_crystals_value_1 = []
                for i in range(len(response_json["response"]["crystals"])):
                    crystals_uid_1 = response_json["response"]["crystals"][i]["uid"]
                    crystals_value_1 = response_json["response"]["crystals"][i]["value"]
                    list_crystals_uid_1.append(crystals_uid_1)
                    list_crystals_value_1.append(crystals_value_1)
                    sum_crystals_value_1 += crystals_value_1
                averange_crystals_value_1 = sum_crystals_value_1 / len(response_json["response"]["crystals"])

                plt.figure(figsize=(14, 9))
                plt.title("chinese service crystals list")
                plt.xlabel("nickname")
                plt.ylabel("amount")
        # plt.xticks(np.arange(1, len(collage_sort_drop_duplication) + 1),collage_sort_drop_duplication.to_numpy().tolist())
                plt.grid(ls=":", lw="1", color="blue")
                plt.axhline(averange_crystals_value_1, color="red", label="averange" + str(averange_crystals_value_1), lw=2)
                plt.plot(list_crystals_uid_1, list_crystals_value_1, color="k", label="crystals amount", lw=2)
                plt.legend()

                plt.savefig("guofushuijingbang.png")

                '''await message.reply(file_image="guofushuijingbang.png")'''
                #await message.reply(content=list_crystals_uid_1[1:10])
                if message.guild_id != "16488793382617768689":
                    await message.reply(file_image="guofushuijingbang.png")
                else:
                    await message.reply(content="本频道无法使用该机器人，请加主频道1xsqbm99k4并联系频道主testanki")
                    await message.reply(file_image="JS.jpg")
        except Exception:

            print("国服水晶榜查询错误")


        try:
            if message.content[0:29] == "<@!15425887405726406995> /天气 ":
                respones_province_url = ''
                province_in = re.findall('<@!15425887405726406995> /天气 (.*?)#', message.content, re.S)
                url_all_province = "http://www.nmc.cn/rest/province/all"
                header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
                respones_province = requests.get(url=url_all_province, headers=header)
                respones_province_code = re.findall('name":"(.*?)","url', respones_province.text, re.S)

                for i in range(len(respones_province_code)):
                    if province_in[0] == respones_province_code[i]:
                        respones_province_url = re.findall('url":"(.*?)"}', respones_province.text, re.S)[i]

                url_city = "http://www.nmc.cn/rest/province/" + \
                           re.findall('/publish/forecast/(.*?).html', respones_province_url, re.S)[0]
                print(url_city)
                response_city = requests.get(url=url_city, headers=header)

                city_in = re.findall('#(.*?)#', message.content, re.S)
                response_city_name = re.findall('city":"(.*?)","url', response_city.text, re.S)
                p = Pinyin()
                city_pinyin_li = p.get_pinyin(city_in[0]).split("-")
                city_pinyin = ""
                for i in range(len(city_pinyin_li)):
                    city_pinyin = city_pinyin + city_pinyin_li[i]
                url = 'http://www.nmc.cn/publish/forecast/' + \
                      re.findall('/publish/forecast/(.*?).html', respones_province_url, re.S)[
                          0] + '/' + city_pinyin + '.html'
                print(url)

                # print(response_city_name)下面的几行暂时不需要
                '''
                for i in range(len(response_city_name)):
                    if city_in==response_city_name[i]:
                        response_city_url='http://www.nmc.cn/rest/weather?stationid='+re.findall('code":"(.*?)","province":"安徽省",',response_city.text,re.S)[i]
                        print(response_city_url)
                '''

                # response_city_code=re.findall()

                header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
                respones = requests.get(url=url, headers=header)
                # pprint.pprint(respones.text)

                html = etree.HTML(respones.text)
                day = html.xpath('//*[@id="day7"]/div[1]/div/div[1]/text()[1]')[0]

                # week_day=html.xpath('//*[@id="day7"]/div[1]/div/div[1]/text()[2]')[0]
                hour = html.xpath('//*[@id="day0"]/div[1]/div[1]')[0].text

                # print(hour)
                temp = html.xpath('//*[@id="day0"]/div[1]/div[4]')[0].text  # //*[@id="day0"]/div[1]/div[4]
                temp_print = temp[0:5] + "摄氏度"
                sunny_rain_url = html.xpath('//*[@id="day0"]/div[1]/div[2]/img/@src')[0]
                imp = re.findall("http://image.nmc.cn/assets/img/w/40x40/3/(.*?).png", sunny_rain_url, re.S)[0]
                # print(imp)
                sunny_rain_msg = {"0": "晴", "1": "多云", "2": "阴", "3": "阵雨", "4": "雷阵雨", "5": "雨夹冰雹",
                                  "6": "雨夹雪", "7": "小雨", "8": "中雨", "9": "大雨", "10": "暴雨", "11": "大暴雨"}
                sunny_rain = sunny_rain_msg.get(imp, "错误")
                # print(sunny_rain)
                # print(imp)

                moisture = html.xpath('//*[@id="day0"]/div[1]/div[8]')[0].text
                # air_quality=html.xpath('//*[@id="aqi"]/@text')[0]

                # print(air_quality)

                # print(messages)
                # use_data=0
                # for i in range(len(messages)):
                # use_data=use_data+messages[i]
                nmc_data = city_in[0] + '\n' + '日期：' + day + '\n' + '小时：' + hour + '\n' + '温度：' + temp_print + '\n' + '天气状态：' + sunny_rain + '\n' + '湿度：' + moisture
                await message.reply(content=nmc_data)
        except Exception:
            print("天气错误")


        try:
            if message.content[0:31] == "<@!15425887405726406995> /国服装备 ":
                names = message.content[31:]
                url = 'https://ratings.3dtank.com/get_stat/profile/?user=' + names + '&lang=cn'
            elif message.content[0:31] == "<@!15425887405726406995> /外服装备 ":
                names = message.content[31:]
                url = "https://ratings.tankionline.com/api/eu/profile/?user=" + names + "&lang=cn"

            if message.content[0:31] == "<@!15425887405726406995> /国服装备 " or message.content[0:31] == "<@!15425887405726406995> /外服装备 ":

                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
                response = requests.get(url=url, headers=header)

                json_data = json.loads(response.text)
                #pprint.pprint(json_data)
                if json_data["responseType"] == "OK":
                    name = re.sub(r"\.","。",json_data['response']['name'])
                    if json_data["response"]["hasPremium"] == True:
                        name = "[VIP] " + name
                    rank = json_data['response']['rank']
                    rank_true = rank - 1
                    to_rank_list = ['新兵', '二等兵', '一等兵', '下士', '中士', '上士',
                                    '三级军士长', '二级军士长', '一级军士长', '军士长',
                                    '五级准尉',
                                    '四级准尉', '三级准尉', '二级准尉', '一级准尉',
                                    '特级准尉', '少尉', '中尉', '上尉', '少校',
                                    '中校', '上校', '准将', '少将', '中将',
                                    '上将', '元帅', '陆军元帅', '统帅', '大元帅']
                    if rank_true <= 29:
                        rank_name = to_rank_list[rank_true]

                    else:
                        rank_name = "传奇" + str(rank_true - 29)
                    gearscore = json_data['response']['gearScore']

                    def equipment(json_data, mod, index):
                        turret_msg_list = []
                        t = ""
                        for i in range(len(json_data["response"][mod])):
                            turret_name = json_data["response"][mod][i]["name"]
                            turret_id_list = []
                            for j in range(len(json_data["response"][mod])):
                                if json_data["response"][mod][j]["name"] == turret_name:
                                    turret_id = json_data["response"][mod][j]["grade"]
                                    turret_id_list.append(turret_id)
                            turret_grade = max(turret_id_list)
                            if index == 1:
                                turret_data = turret_name + ':' + str(turret_grade + 1)+' '
                            else:
                                turret_data = turret_name + ':' + "Nan"+' '
                            if turret_data in turret_msg_list:
                                continue
                            turret_msg_list.append(turret_data)
                        return turret_msg_list


                    turret = equipment(json_data=json_data, mod='turretsPlayed', index=1)
                    hull = equipment(json_data=json_data, mod='hullsPlayed', index=1)
                    drone = equipment(json_data=json_data, mod='dronesPlayed', index=0)
                    module = equipment(json_data=json_data, mod='resistanceModules', index=0)
                    datas = (name+'\n'+"等级："+rank_name+'\n'+'战力GS：' + str(gearscore) +'\n' + "-------炮塔-------" + '\n' + ','.join(turret) + '\n' + "-------底盘-------" + '\n' + ','.join(
                            hull) + '\n' + '-------无人机-------' + '\n' + ','.join(drone) + '\n' + '-------模块-------' + '\n' + ','.join(module))
                    if message.guild_id != "16488793382617768689":
                        await message.reply(content=datas)
                    else:
                        await message.reply(content="本频道无法使用该机器人，请加主频道1xsqbm99k4并联系频道主testanki")
                        await message.reply(file_image="JS.jpg")
                    '''await message.reply(content=datas)'''
                else:
                    await message.reply(content="未查询到数据，可能开启隐藏数据或输入不正确")
        except Exception:
            await message.reply(content="机器人工作异常/网站连接异常/频道拦截消息")

        try:
            if message.content[0:31] == "<@!15425887405726406995> /随机事实 ":

                with open("facts.json", 'r', encoding='utf-8') as f:
                    fact_json = json.load(f)
                fact = fact_json[random.randint(0, len(fact_json))]["en"]
                await message.reply(content=fact)
        except Exception:
            print("失败")

        try:
            if message.content[0:29] == '<@!15425887405726406995> 装备升级':
                equip_name=message.content[29:]
                headers = {
                    "authority": "en.tankiwiki.com",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "sec-ch-ua": 'Not A(Brand";v="99", "Microsoft Edge";v="121,Chromium";v="121',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
                }
                cookies = {
                    "_ym_uid": "1702000361954175054",
                    "_ym_d": "1702000361",
                    "_ym_isad": "1",
                    "TCK2": "9a1bb93cb19384b86f5f4069e7266a9a"
                    # 和梯子节点有关#9a1bb93cb19384b86f5f4069e7266a9a#c1b0e3c901feaae99986951e2064f3aa
                }
                url = "https://en.tankiwiki.com/Micro-upgrades_"+equip_name
                response = requests.get(url, headers=headers, cookies=cookies)

                print(response)
                if response.status_code==200:
                    htmldata = etree.HTML(response.text)
                    micro_upgrade = ''
                    for mk_rank in range(2,9):  # //*[@id="mw-content-text"]/div[1]/table[8]/tbody/tr/td[2]/ul/li[1]/text()[1]
                        i = 0
                        grade = 'MK' + str(mk_rank - 1) + '→MK' + str(mk_rank) + '\n'
                        micro_upgrade += grade
                        per_grade = ''
                        while True:
                            i += 1
                            damage_list = htmldata.xpath(
                                '//*[@id="mw-content-text"]/div[1]/table[' + str(mk_rank) + ']/tbody/tr/td[2]/ul/li[' + str(
                                    i) + ']/text()[1]') + htmldata.xpath(
                                '//*[@id="mw-content-text"]/div[1]/table[' + str(mk_rank) + ']/tbody/tr/td[2]/ul/li[' + str(
                                    i) + ']/text()[2]')
                            # print(''.join(damage_list))
                            per_grade += '\t' + ''.join(damage_list) + '\n'
                            if len(damage_list) == 0:
                                micro_upgrade += per_grade
                                break
                    await message.reply(content=equip_name+'\n'+micro_upgrade)
                elif response.status_code==202:
                    await message.reply(content="网络故障")
                elif response.status_code==404:
                    await message.reply(content="装备名称输入错误，请输入装备的英文名，注意首字母大写")
        except Exception:
            await message.reply(content="机器人工作异常/频道拦截消息")


        try:
            if message.content[0:29] == '<@!15425887405726406995> 近期在线':

                df = pd.read_csv('onlinedata.csv', encoding='gbk')
                time_stamp = df['时间'].tolist()[-135:]

                inbattle = df['战斗中'].tolist()[-135:]
                online = df['国服在线'].tolist()[-135:]
                online_4399 = df['4399在线'].tolist()[-135:]

                time_true_list = []
                for j in range(len(time_stamp)):
                    day = str(time.localtime(time_stamp[j]).tm_mday)
                    hour = str(time.localtime(time_stamp[j]).tm_hour)
                    minute = str(time.localtime(time_stamp[j]).tm_min)
                    time_true = day + '日' + hour + '时' + minute + '分'
                    time_true_list.append(time_true)

                inbattle_online_list = []
                for i in range(len(online)):
                    inbattle_online = inbattle[i] / online[i]
                    inbattle_online_list.append(inbattle_online)

                fig, ax1 = plt.subplots(figsize=(2560 / 80, 1440 / 80), dpi=80)
                plt.rcParams['font.sans-serif'] = ['SimHei']  # SimHei 是支持中文的字体，你可以根据需要选择其他字体
                plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
                plt.title('国服在线人数情况')

                color = 'tab:blue'
                ax1.set_xlabel('时间')
                ax1.set_ylabel('战斗中', color=color)
                ax1.set_ylabel('人数')
                xticks = plt.xticks(np.arange(0, len(time_true_list), 1), rotation=90, ha="right")
                yticks = ax1.set_yticks(np.arange(0, max(online) + 10, 10))
                ax1.set_xlim(0, len(time_true_list) - 2)
                ax1.set_ylim(0, max(online) + 10)
                ax1.grid(True, linestyle='--', alpha=0.7)
                line_inbattle = ax1.plot(time_true_list, inbattle, marker='+', linestyle='-', color='b', label='战斗中')
                line_online = ax1.plot(time_true_list, online, marker='.', linestyle='-.', color='y', label='游戏在线')
                line_online4399 = ax1.plot(time_true_list, online_4399, marker='*', linestyle=':', color='g',
                                           label='4399在线')
                ax1.legend(loc='upper right')

                ax2 = ax1.twinx()
                color = 'tab:red'
                ax2.set_ylabel('战斗中与在线比例', color=color)
                ax2.set_yticks(np.arange(0, 1, 0.01))
                ax2.set_ylim(0, 1)
                line_scale = ax2.plot(time_true_list, inbattle_online_list, marker='d', linestyle='--', color=color,
                                      label='战斗中占比')
                ax2.tick_params(axis='y', labelcolor=color)

                lines, labels = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines + lines2, labels + labels2, loc='upper right')

                # 显示图表
                plt.tight_layout()  # 防止标签被截断
                plt.savefig('my_plot.png')
                await message.reply(file_image="my_plot.png")
        except Exception:
            await message.reply(content="机器人工作异常/频道拦截消息")


'''        #try:
        if message.content[0:29] == "<@!15425887405726406995> /评分 ":
                user_name=message.content[29:]
                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

                names = [user_name,"shenzhou", "xiaoli17", "parousia", "gan356", "Mercury-XG", "xiaoli4", "00087g", "ergic",
                         "akuma.yanwu", "chutong", "jumper", "weallive", "rtjly"]
                column = ["ID", "KD", "经验效率", "分数效率", "道具效率"]
                df = pd.DataFrame(columns=column)

                column_c = ["ID", "f"]
                df_c = pd.DataFrame(columns=column_c)

                list = []
                for num in range(len(names)):
                    name = names[num]
                    url = "https://ratings.tankionline.com/api/eu/profile/?user=" + name + "&lang=en"
                    response = requests.get(url=url, headers=header)
                    json_data = json.loads(response.text)
                    if num == 0:
                        id_us=json_data['response']['name']
                    id = json_data['response']['name']
                    kills = json_data['response']['kills']
                    deaths = json_data['response']['deaths']

                    rank = json_data['response']['rank'] - 1
                    exp_base = json_data['response']['scoreBase']

                    sum_score = 0
                    sum_time = 0
                    for i in range(11):
                        score_mode = json_data['response']["modesPlayed"][i]["scoreEarned"]
                        sum_score += score_mode
                        time_mode = json_data['response']["modesPlayed"][i]["timePlayed"]
                        sum_time += time_mode

                    sum_supply = 0
                    for i in range(7):
                        supplies_element_usage = json_data['response']['suppliesUsage'][i]['usages']
                        sum_supply += supplies_element_usage

                    kd = kills / deaths  # KD
                    exp_time = exp_base / sum_time  # 经验效率
                    score_time = sum_score / sum_time  # 分数效率
                    supply_time = sum_supply / sum_time
                    supply_time_t = 1 / supply_time  # 道具效率（已经变为效益型）

                    list = [id, kd, exp_time, score_time, supply_time_t]
                    df.loc[(num + 2), column] = list
                #df.to_csv("test1.csv")

                kd_max = np.max(df["KD"])
                exp_time_max = np.max(df["经验效率"])
                score_time_max = np.max(df["分数效率"])
                supply_time_t_max = np.max(df["道具效率"])

                max_list = [kd_max, exp_time_max, score_time_max, supply_time_t_max]
                weight_list = [0.4, 0.2, 0.2, 0.2]
                for index, row in df.iterrows():
                    for column_index in range(1, len(df.columns)):
                        value = df.iloc[index - 2, column_index]
                        value_b = value / max_list[column_index - 1] * weight_list[column_index - 1]
                        # print(max_list[column_index-1])
                        df.iloc[index - 2, column_index] = value_b

                max_list_c = []
                min_list_c = []
                kd_min = np.min(df["KD"])
                exp_time_min = np.min(df["经验效率"])
                score_time_min = np.min(df["分数效率"])
                supply_time_t_min = np.min(df["道具效率"])
                min_list_c = [kd_min, exp_time_min, score_time_min, supply_time_t_min]

                kd_max = np.max(df["KD"])
                exp_time_max = np.max(df["经验效率"])
                score_time_max = np.max(df["分数效率"])
                supply_time_t_max = np.max(df["道具效率"])
                max_list_c = [kd_max, exp_time_max, score_time_max, supply_time_t_max]

                for index, row in df.iterrows():
                    sum_max = 0
                    sum_min = 0
                    for column_index in range(1, len(df.columns)):
                        value = df.iloc[index - 2, column_index]
                        value_c_max = (value - max_list_c[column_index - 1]) ** 2
                        sum_max += value_c_max
                        value_c_min = (value - min_list_c[column_index - 1]) ** 2
                        sum_min += value_c_min
                    distance_sum_max = pow(sum_max, 0.5)
                    distance_sum_min = pow(sum_min, 0.5)
                    f = distance_sum_min / (distance_sum_max + distance_sum_min)
                    df_c.loc[index - 2, ["f"]] = f
                    df_c.loc[index - 2, ["ID"]] = row
                df_c_sort=df_c.sort_values(by="f", ignore_index=True)
                #df_c_sort.to_csv("test.csv")
                for i in range(len(df_c_sort["ID"])):
                    #print(df_c_sort.loc[i,"ID"])
                    if df_c_sort.loc[i,["ID"]].values==id_us:
                        row_index=i+2
                        break
                #print(row_index)
                grade=(row_index/len(df_c_sort["ID"]))*100

                await message.reply(content=str(grade)+"\n"+"评分依据：KD:40%，经验/匹配时间:20%，分数/匹配时间:20%，道具用量/匹配时间:20%")
        #except Exception:
            #await message.reply(content="评分失败，注意只能对外服评分")'''
if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])