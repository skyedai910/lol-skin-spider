# 30行Python代码爬取英雄联盟全英雄全皮肤

## 碎碎念

英雄联盟游戏里拥有数百个个性英雄，然后每个英雄都有多个皮肤。作为一个收集控就非常想收齐全部皮肤----的图片。家境贫寒~一言难尽~看官点个赞呗！

## 前期分析

英雄皮肤的图鉴信息可以到官网游戏资料（``https://lol.qq.com/data/info-heros.shtml``）查看到。

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114120137.png)

爬取皮肤本身难度不大，就是将数据以二进制形式保存到文件中。难点是怎么拿到皮肤图片的URL地址。马上到官网，点开几个英雄皮肤分析一下。

随意选择一位英雄，然后F12打开调试台，找到英雄皮肤的图片地址：

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114120339.png)

找到皮肤图片位置，然后我们多找几个皮肤图片地址来对比分析，找到其中的规律：

```
英雄一
https://game.gtimg.cn/images/lol/act/img/skin/big1000.jpg
https://game.gtimg.cn/images/lol/act/img/skin/big1001.jpg
https://game.gtimg.cn/images/lol/act/img/skin/big1002.jpg
英雄二
https://game.gtimg.cn/images/lol/act/img/skin/big2000.jpg
https://game.gtimg.cn/images/lol/act/img/skin/big2001.jpg
https://game.gtimg.cn/images/lol/act/img/skin/big2002.jpg
```

这里对比分析两个英雄的3个皮肤图片地址，发现只有最后的序号发生变换，猜测皮肤图片的地址通用格式为``https://game.gtimg.cn/images/lol/act/img/skin/bigxxxx.jpg``。序号部分规律应该是最前一位数字代表着英雄的编号，后三位的数字代表该英雄的皮肤编号。

```
x       xxx
英雄编号 皮肤编号
```

按照这个规律，我们就能将全部的英雄皮肤图片地址推算出来。但。。。。实际上，英雄编号并不是依次递增的。比如说新英雄瑟提的编号为875，而实际上瑟提为正式服的第148位英雄。

这样一来，视乎英雄编号就没有什么规律了。别急，在英雄资料页，打开F12调试台，抓取网络请求，发现了几个文件。居然有一个hero_list.js文件。这个json文件里面存放的正是我们苦苦寻找的英雄编号：

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114122118.png)

英雄编号有了，那么下一步就是寻找英雄的皮肤编号了。因为每个英雄的皮肤数量不同，同一个皮肤还可能有炫彩皮肤，通过html文件正则匹配出来不是不行，只是懒~那尝试一下找找英雄详情页有没有类似与hero_list.js的文件。

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114122635.png)

这不是刚刚好了么XD~每个英雄有一个以英雄编号为前缀的json文件，里面记录着有该英雄的皮肤图片地址。其中的mainImg为皮肤大图、iconImg为皮肤头像。json文件中还记录着英雄的其他信息如：定位、技能、描述等等。可以自己尝试爬取下来，作用。。。。自行开发。

既然每个英雄的json文件中存有皮肤图片的地址，那就不需要我们自己构建英雄皮肤图片的地址，而是构建英雄json请求链接，从json中解析出来皮肤图片地址。

## 代码实现

需要用到os、requests库。第一步获取英雄编号的json文件。文件地址为：``https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js``，请求方式为get。这个地址可以在调试台中找到。获取json文件后，然后解析json数据，将英雄编号提取出来。

```python
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
```

拿到英雄编号后，就需要构建出英雄独立json的地址，通用格式为：``https://game.gtimg.cn/images/lol/act/img/js/hero/【英雄编号】.js``。get请求地址获取英雄独立json文件，从文件中解析出皮肤地址：

```python
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
```

当中有两个错误处理，一个是创建每个英雄独立文件夹；另外一个是处理炫彩皮肤。因为炫彩皮肤没有独立做的大图，所以json中并没有皮肤大图链接。

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114130809.png)

## 结尾

去除注释空行，近30行的代码即可将英雄联盟全英雄全皮肤图片爬取下来。先来看看成品吧~

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114131037.png)

![](https://raw.githubusercontent.com/skyedai910/Picbed/master/img/20200114131056.png)

### 完整代码

写代码的时候，文件夹创建用的是相对路径，创建在程序运行的目录下，所以请在源码所在目录下启动cmd（powershell）运行，否则文件夹创建位置不可预期。

```python
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
```

