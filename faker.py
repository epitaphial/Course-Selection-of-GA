# -*- coding: gbk -*-
import configparser
import itertools
import os
import random
import numpy as np
import math
from random_name import random_chinese_name

class Faker:
	def __init__(self,configName):
		self.cf = configparser.ConfigParser()

		self.cf.add_section("trans")

		self.cf.set("trans","basic","基本配置")
		self.cf.add_section("basic")

		self.cf.set("trans","room","教室配置")
		self.cf.add_section("room")

		self.cf.set("trans","subject","科目配置")		
		self.cf.add_section("subject")

		self.cf.set("trans","techclass","教学班配置")		
		self.cf.add_section("techclass")

		self.cf.set("trans","admclass","行政班配置")
		self.cf.add_section("admclass")

		self.cf.set("trans","teacher","教师配置")		
		self.cf.add_section("teacher")
		self.confName = configName

# 生成和固定的随机数列表
	def sumDef(self,sumNum,num):
		sumBef = np.random.randint(num,sumNum,size=num-1)
		ratio = sum(sumBef)/sumNum
		sumAft = sumBef//ratio
		sumAft = sumAft.tolist()
		sumAft.append(sumNum-sum(sumAft))
		return sumAft

# 基础配置
	def basic_deal(self):
		#self.totalTime = random.randint(7,9)*5
		self.totalTime = 35
		self.cf.set("basic","totaltime",str(self.totalTime))
		self.cf.set("trans","totaltime","每周总的教学时间")	

# 教室配置
	def room_deal(self):
		roomNum = random.randint(30,40)
		self.cf.set("room","roomnum",str(roomNum))
		self.cf.set("trans","roomnum","教室数量")	
		self.cf.set("trans","roomid","教室编号")
		roomCap = {}
		for i in range(roomNum):
			roomCap["roomid"+str(i+1)] = random.randint(50,60)
		self.cf.set("room","roomcap",str(roomCap))
		self.cf.set("trans","roomcap","教室容量")

# 科目配置
	def subject_deal(self):
		subNum = 9
		self.cf.set("trans","subnum","科目数量")
		self.cf.set("subject","subnum",str(subNum))
		self.subDict = {"sub1":"语文","sub2":"数学","sub3":"英语","sub4":"物理","sub5":"化学","sub6":"生物","sub7":"政治","sub8":"历史","sub9":"地理"}
		self.cf.set("trans","eng2chi",str(self.subDict))
		self.cf.set("trans","subinfo","科目信息")
		self.cf.set("trans","subid","科目编号")
		self.cf.set("trans","submark","科目学分")
		self.cf.set("trans","subtime","每周科目学时")
		times = self.sumDef(self.totalTime-10,subNum)
		listSub = []
		for i in range(subNum):
			mark = random.randint(1,5)
			dictA = {'subid':'sub'+str(i+1),'submark':str(mark),'subTime':str(int(times[i]))}
			listSub.append(dictA)
		self.cf.set("subject","subinfo",str(listSub))

# 分科函数
	def divSub(self):
		list1 = ['sub4','sub5','sub6','sub7','sub8','sub9']
		list2 = []
		for i in range(1,len(list1)+1):
			iter = itertools.combinations(list1,i)
			if i == 3:
				list2.append(list(iter))
		return list2[0]


# 教学班配置
	def techclass_deal(self):
		classNum = 20
		self.cf.set("techclass","techclassnum",str(classNum))
		self.cf.set("trans","techclassnum","教学班数量")	
		self.cf.set("trans","techclassid","教学班编号")
		classStu = {}
		classInfo = {}
		divList = self.divSub()
		self.totalStu = 0
		for i in range(classNum):
			classInfo["techclassid"+str(i+1)] = divList[i]
			tmpStu = random.randint(20,30)
			classStu["techclassid"+str(i+1)] = tmpStu
			self.totalStu += tmpStu
		self.cf.set("trans","techclassinfo",str(classInfo))
		self.cf.set("techclass","techclassstu",str(classStu))
		self.cf.set("trans","techclassStu","教学班人数")
		self.cf.set("trans","totalstu","学生总人数")
		self.cf.set("basic","totalstu",str(self.totalStu))

# 行政班配置
	def admclass_deal(self):
		standardStu = random.randint(40,50)
		self.cf.set("admclass","standardadm",str(standardStu))
		self.cf.set("trans","standardadm","每个行政班标准人数")
		totalAdm = int(math.ceil(self.totalStu/standardStu))
		self.cf.set("trans","admclassnum","行政班个数")
		self.cf.set("admclass","admclassnum",str(totalAdm))
		admclassInfo = {}
		for i in range(totalAdm-1):
			admclassInfo['admclass'+str(i+1)] = standardStu
		admclassInfo['admclass'+str(totalAdm)] = self.totalStu - standardStu*(totalAdm-1)
		self.cf.set("admclass","admclassinfo",str(admclassInfo))
		self.cf.set("trans","admclassinfo","各个行政班人数")

# 教师配置
	def teacher_deal(self):
		teacherNum = random.randint(40,50)
		self.cf.set("teacher","teachernum",str(teacherNum))
		self.cf.set("trans","teachernum","教师数量")
		dictTN = {}
		dictTC = {}
		for i in range(9):
			dictTN["teacher"+str(i+1)] = random_chinese_name()
			dictTC["teacher"+str(i+1)] = "sub"+str(i+1)
		for i in range(9,teacherNum):
			dictTN["teacher"+str(i+1)] = random_chinese_name()
			dictTC["teacher"+str(i+1)] = random.sample(self.subDict.keys(),1)[0]

		self.cf.set("trans","teacherinfo","教师信息")
		self.cf.set("trans","teacherid",str(dictTN))
		self.cf.set("teacher","teacherinfo",str(dictTC))


	def exec(self):
		self.basic_deal()
		self.room_deal()
		self.subject_deal()
		self.techclass_deal()
		self.teacher_deal()
		self.admclass_deal()
		with open(self.confName,'w+') as f:
			self.cf.write(f)

faker = Faker('config.ini')
faker.exec()
if os.path.exists('config.ini'):
	print("Success!")
else:
	print("oooooops,Something Wrong...QAQ")