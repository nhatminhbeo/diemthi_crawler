import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display

import json
import re
import lxml
from bs4 import BeautifulSoup
import time
import requests

#####################################################################################
#																					#
#									Functions										#
#																					#
#####################################################################################
#dummy wait
def dummywait(time):
	try:
		WebDriverWait(driver, time).until(EC.visibility_of_element_located((By.CLASS_NAME, "dummywait")))
	except:
		dummy = 0
	finally: 
		dummy = 0

def getStudent(url,sbd):
	student = []
	r = requests.get(url + sbd)
	res = r.json()
	if (res["message"] == "success"):
		student.append(sbd)
		student.append(res["result"].encode('utf-8'))
		return student
	else:
		return None


def readProvince(fname):
	p2c = {}
	c2p = {}
	f = open(fname, "r")
	for line in f:
		words = line.split()
		p = words[0]
		c = words[1]
		p2c[p] = c
		c2p[c] = p
	f.close()
	return p2c, c2p


# write to file the next student
def writeResult(f, student):
	line = ""
	first = True
	for s in student:
		if (not first):
			line = line + ","
		first = False
		line = line + s
		
	line = line + "\n"
	f.write(line)

#####################################################################################
#																					#
#									Arguments										#
#																					#
#####################################################################################
if len(sys.argv) != 6:
	print('WRONG ARGUMENTS')
	print('USAGE:')
	print('$python crawler.py [MAX_SKIP] [MA_TINH x 2 digits] [SBD_BAT_DAU x 6 digits] [SBD_KET_THUC x 6 digits] [DEBUG=T/F]')
	sys.exit()


MAX_SKIP = int(sys.argv[1])
MA_TINH = sys.argv[2]
SBD_BAT_DAU = sys.argv[3]
SBD_KET_THUC = sys.argv[4]
DEBUG = True if (sys.argv[5] == "T") else False
HEADER = "SBD,Diem\n"
URL = "https://diemthi.vietnamplus.vn/Home/Search?id="


#####################################################################################
#																					#
#									Main Script										#
#																					#
#####################################################################################

if (DEBUG):
	print("Starting script ...")

if (DEBUG):
	print("Reading Province Code ...")

p2c, c2p = readProvince("ma_tinh.txt")

stat = {"STATUS":"started", "MA_TINH": MA_TINH, "TINH": c2p[MA_TINH], "SBD_BAT_DAU": SBD_BAT_DAU, "SBD_KET_THUC": "SBD_KET_THUC"}
r = requests.post('https://vietego-zing-crawler.herokuapp.com/1cma06m1', data=stat)

NEW = True
if os.path.isfile("data/%s_%s_%s_%s.csv" % (MA_TINH,c2p[MA_TINH],SBD_BAT_DAU, SBD_KET_THUC)):
	NEW = False
f = open("data/%s_%s_%s_%s.csv" % (MA_TINH,c2p[MA_TINH],SBD_BAT_DAU, SBD_KET_THUC), "a+")
if NEW:
	f.write(HEADER)

if (DEBUG):
	print("Starting crawler ...")
skips = 0
loop_time = time.time()
for i in range(int(SBD_BAT_DAU), int(SBD_KET_THUC) + 1):
	SBD = "%s%06d" % (MA_TINH,i)
	if (skips > MAX_SKIP):
		print("MAX_SKIP %d reached" % MAX_SKIP)
		break
	start_time = time.time()
	student = getStudent(URL,SBD)
	if(DEBUG):
		print(student)
	if student is None:
		skips = skips + 1
	else:
		skips = 0
		writeResult(f, student)
	if (DEBUG):
		print("Done %s in %fs" % (SBD,time.time() - start_time))
print("Done ALL from %s to %s of %s:%s in %fs" % (SBD_BAT_DAU, SBD_KET_THUC, MA_TINH, c2p[MA_TINH], time.time() - loop_time))

f.close()

stat = {"STATUS":"done", "MA_TINH": MA_TINH, "TINH": c2p[MA_TINH], "SBD_BAT_DAU": SBD_BAT_DAU, "SBD_KET_THUC": "SBD_KET_THUC", "LOOP_TIME": time.time() - loop_time}
r = requests.post('https://vietego-zing-crawler.herokuapp.com/1jdqvsj1', data=stat)


