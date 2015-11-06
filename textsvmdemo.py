# -*- coding: utf-8 -*-
from traintext import train_src
# train_src = []
sample_titles = []
with open('infoq.txt') as fp:
    for line in fp.readlines():
        params = line.split('|')
        if len(params)>=2:
            tag = params[0]
            title = params[1]   
            #train_src.append((tag, title))
        else:
            sample_titles.append(line)


from textgrocery import Grocery
# 新开张一个杂货铺，别忘了取名！
grocery = Grocery('codernews')

grocery.train(train_src)
# 也可以用文件传入
#grocery.train('train_ch.txt')
# 保存模型
grocery.save()
# 加载模型（名字和保存的一样）
new_grocery = Grocery('codernews')
new_grocery.load()
# 预测
with open('out.txt', "w") as fp:
    for title in sample_titles:
        tag = new_grocery.predict(title)
        print(tag, title)
        fp.write("%s ==> %s\n" % (tag, title))

fp.close()