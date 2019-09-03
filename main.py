import configparser
import os
import random

# 读配置文件
def readConf(configFile,subject,key):
	cf = configparser.ConfigParser()
	filename = cf.read(configFile)
	return cf.get(subject,key)

# 根据班级类型返回列表
def pro2list(classId):
	classList = eval(readConf('config.ini','trans','techclassinfo')) # 教学班信息
	subInfo = eval(readConf('config.ini','subject','subinfo')) # 学科信息	
	if classId == 'admclass':
		listClass = []
		for s in range(3):
			for i in range(int(subInfo[s]['subTime'])):
				listClass.append('sub'+str(s+1))
	else:
		classTp = classList[classId]
		listClass = []
		for s in range(3):
			for i in range(int(subInfo[int(classTp[s][3])-1]['subTime'])):
				listClass.append(classTp[s])
	return listClass


# 基因类
class Gene:
	def __init__(self,roomId,courseId,teacherId):
		self.room_id = roomId
		self.course_id = courseId
		self.teacher_id = teacherId
	
	def tupleGene(self):
		return (self.course_id,self.teacher_id,self.room_id)

# 染色体类
class Chromosome:
	def __init__(self,row,col):
		self.init_list = [["0"]*col for _ in range(row)]


# GA类
class GA:
	def __init__(self):
		self.population = [] # 种群
		self.teacher_info = eval(readConf('config.ini','teacher','teacherinfo')) # 教师信息
		self.teacher_num = int(readConf('config.ini','teacher','teachernum'))
		self.room_info = eval(readConf('config.ini','room','roomcap')) # 教室信息
		self.sub_info = eval(readConf('config.ini','subject','subinfo')) #学科信息
		self.admclass_num = int(readConf('config.ini','admclass','admclassnum')) # 行政班数量
		self.techclass_num = int(readConf('config.ini','techclass','techclassnum')) # 教学班数量
		self.totalclass_num = self.admclass_num + self.techclass_num
		self.totalPeriod = int(readConf('config.ini','basic','totaltime'))
		self.room_num = int(readConf('config.ini','room','roomnum'))
		self.admclass_info = eval(readConf('config.ini','admclass','admclassinfo'))
		self.techclass_info = eval(readConf('config.ini','techclass','techclassstu'))
		self.subc2e_info = eval(readConf('config.ini','trans','eng2chi'))
		self.teacher_name = eval(readConf('config.ini','trans','teacherid'))

# 种群生成	
	def makePopulation(self):
		print("start make population...")
		self.markArray = []
		times = 0 # 迭代次数
		while True:
			chrs = Chromosome(self.totalclass_num,self.totalPeriod) # 染色体
			for i in range(1,self.totalclass_num+1): #每个班级
				if i <= self.admclass_num:
					listClass = pro2list('admclass')
				else:
					listClass = pro2list('techclassid'+str(i-self.admclass_num))
				seq = [i for i in range(self.totalPeriod)]
				randNumList = random.sample(seq,len(listClass)) #随机选择课程
				count =0
				for randNum in randNumList:
					randomRoom = random.randint(1,self.room_num) #随机选择教室
					listableTeacher = []
					for q in range(self.teacher_num):
						if self.teacher_info["teacher"+str(q+1)] == listClass[count]:
							listableTeacher.append("teacher"+str(q+1))
					geneTmp = Gene("roomid"+str(randomRoom),listClass[count],listableTeacher[random.randint(0,len(listableTeacher)-1)])
					chrs.init_list[i-1][randNum] = geneTmp.tupleGene()
					count+=1
			tmpHard = self.hard_check(chrs.init_list)
			if tmpHard != False:		
				chrs.init_list = tmpHard
				self.population.append(self.encode(tmpHard))
				times+=1
				#print(chrs.init_list)
				self.softMark(chrs.init_list)
				self.output(chrs.init_list)

			if times >= 10:# 迭代次数
				print("added %d Chromosome" %times)
				break

# 评估函数,杂交变异
	def softMark(self,biglist):
		markTemp = 0

		# 节次优度评估
		noArray = [0.94,0.94,0.85,0.85,0.65,0.65,0.55,0.55] # 节次优度表
		for x in biglist:
			colTp = 0
			for y in x:
				if y != "0":
					mt = int(colTp%(self.totalPeriod/5))
					colTp+=1
					markTemp += noArray[mt]*int(self.sub_info[(int(y[0][3])-1)]['submark']) #学分乘以节次优度，求和
		
		# 科目均匀评估
		print(markTemp)
		self.markArray.append(markTemp)

	def mixPlay(self):
		pass


#编码函数,编码规则: hex(course).hex(teacher).hex(room)
	def encode(self,biglist):
		strFin = ""
		for i in biglist:
			for s in i:
				if s == "0":
					strFin+="00000"
				else:
					strFin+=str(hex(int(s[0][3])))[2:]
					if len(str(hex(int(s[1][7:])))[2:]) == 1:
						strFin = strFin + "0" + str(hex(int(s[1][7:])))[2:]
					else:
						strFin += str(hex(int(s[1][7:])))[2:]
					if len(str(hex(int(s[2][6:])))[2:]) == 2:
						strFin+=str(hex(int(s[2][6:])))[2:]
					else:
						strFin = strFin + "0" + str(hex(int(s[2][6:])))[2:]
		return strFin

#解码函数
	def decode(self,bigstr):
		rowS = self.totalclass_num
		colS = self.totalPeriod
		chrs = Chromosome(self.totalclass_num,self.totalPeriod)
		for i in range(0,len(bigstr),5):
			everyStr = bigstr[i:i+5]
			if everyStr != "00000":
				tmpcourseId = int(everyStr[0],16)
				tmpteacherid = int(everyStr[1:3],16)
				tmproomId = int(everyStr[3:],16)
				geneTmp = Gene("roomid"+str(tmproomId),"sub"+str(tmpcourseId),"teacher"+str(tmpteacherid))
				chrs.init_list[int((i/5)//colS)][int((i/5)%colS)] = geneTmp.tupleGene()
			else:
				chrs.init_list[int((i/5)//colS)][int((i/5)%colS)] = "0"
		return chrs.init_list

# 课表打印函数
	def output(self,biglist):
		self.cgedTable = []
		for i in range(self.admclass_num):
			for j in range(self.techclass_num):
				ifB = False
				tmpList = ["0" for i in range(self.totalPeriod)]
				oneTb = [["0" for i in range(5)] for i in range(int(self.totalPeriod/5))]
				admL = biglist[i]
				techL = biglist[self.admclass_num+j]
				for tm in range(self.totalPeriod):
					if admL[tm] != "0" and techL[tm] !="0":
						ifB = True
						break
					elif admL[tm] == "0" and techL[tm] ==0:
						tmpList[tm] = "0"
					elif admL[tm] == "0" and techL[tm] !=0:
						tmpList[tm] = techL[tm]
					else:
						tmpList[tm] = admL[tm]
				if ifB == False:
					for k in range(len(tmpList)):
						oneTb[int(k%(self.totalPeriod/5))][int(k//(self.totalPeriod/5))] = tmpList[k]
					for s in oneTb:
						tmpLen = 0
						for k in s:
							if k == "0":
								s[tmpLen] = "空"
							else:
								s[tmpLen] = self.subc2e_info[k[0]]+self.teacher_name[k[1]]+k[2][6:]+"班"
							tmpLen+=1
					self.cgedTable.append(oneTb)		
#硬约束检查函数
	def hard_check(self,biglist):
		biglist2 = list(map(list, zip(*biglist)))
		for x in biglist2:
			tmpDict = {}
			colNum = 0
			for y in x:
				if y != '0':
					if y[1] not in tmpDict:
						tmpDict[y[1]] = "fuck"
					else:
						ifGet = False
						for i in self.teacher_info:
							if self.teacher_info[i] == y[0] and i not in tmpDict:
								tmpD = list(y)
								tmpD[1] = i
								y = tuple(tmpD)
								tmpDict[i] = "fuck"
								ifGet = True
								break
						if not ifGet:
							return False
					if colNum<self.admclass_num:
						classNum = self.admclass_info['admclass'+str(colNum+1)]
					else:
						classNum = self.techclass_info['techclassid'+str(colNum-self.admclass_num+1)]
					if y[2] not in tmpDict and int(self.room_info[y[2]]) >= int(classNum):
						tmpDict[y[2]] = "fuck"
					else:
						ifGet = False
						for i in self.room_info:
							if self.room_info[i] > classNum and i not in tmpDict:
								tmpD = list(y)
								tmpD[2] = i
								y = tuple(tmpD)
								tmpDict[i] = "fuck"
								ifGet = True
								break
						if not ifGet:
							return False
				colNum+=1
		return list(map(list, zip(*biglist2)))

ga = GA()
ga.makePopulation()
firstOne = ga.cgedTable
with open('result.txt','w+') as f:
	for a in firstOne:
		for b in a:
			strTmp = ""
			for c in b:
				strTmp = strTmp + c +"|"
			strTmp+="\n"
			f.writelines(strTmp)
		f.writelines("\n\n")
			