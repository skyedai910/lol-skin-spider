#encoding:utf-8

import os
import requests

#获取全部英雄json文件
list_url = 'https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js'
herolist = requests.get(list_url)

#处理json文件
herolist_json = herolist.json()#转化为json格式
version = herolist_json['version']#提取版本信息
fileTime = herolist_json['fileTime']#提取json生成时间
heroId = list(map(lambda x:x['heroId'],herolist_json['hero']))#提取英雄Id
#提示信息
print("当前版本为：{}".format(version))
print("英雄列表更新时间为：{}\n".format(fileTime))
print("准备开始下载皮肤....")

#下载每个英雄的皮肤
for heroid in heroId:

	herojs_url = "https://game.gtimg.cn/images/lol/act/img/js/hero/{}.js".format(heroid)
	herojs = requests.get(herojs_url).json()#获取并转换为json文件
	heroname = herojs['hero']['name'] + herojs['hero']['title']#提取英雄称号与别称
	try:
		os.mkdir(heroname)#创建英雄文件夹
		print("\n\n[+] 文件夹【{}】创建成功，开始下载皮肤".format(heroname))
	except FileExistsError:
		print("\n\n[!] 文件夹【{}】已存在，开始下载皮肤".format(heroname))

	for skin in herojs['skins']:
		skinname = skin['name']#提取皮肤名称
		print("[-] 正在下载【{}】".format(skinname))
		skinurl = skin['mainImg']#提取皮肤链接
		#炫彩皮肤错误处理
		try:
			skin_jpg = requests.get(skinurl)
			if skin_jpg.status_code == 200:
				f = open(heroname+"\\"+skinname+".jpg","wb")
				f.write(skin_jpg.content)
				f.close()
		except:
			print("[!] 【{}】为炫彩皮肤无图片".format(skinname))
