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

# get search result of next SBD
def getNext(id):
    # go to url
    driver.find_elements_by_id("txtkeyword")[0].clear()
    driver.find_elements_by_id("txtkeyword")[0].send_keys(id)
        
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "btnresult")))
    element = driver.find_element_by_id('btnresult')
    driver.execute_script("var element = arguments[0]; element.click()", element)

    dummywait(0.05)
    #driver.find_elements_by_id("btnresult")[0].click()
    return BeautifulSoup(driver.page_source, 'lxml')

# get a student from search result
def getStudent(soup):
        try:
            student = []
            soup = soup.find("tbody", {"id": "resultcontainer"})
            soup = soup.find("tr")
            soup = soup.findAll("td")
            for s in soup:
                data = s.text
                student.append(data.encode('utf-8'))
            return student
        except:
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
if len(sys.argv) != 7:
	print('WRONG ARGUMENTS')
	print('USAGE:')
	print('$python crawler.py [DIEM THI LOP 10/12 x 2 digits] [MAX_SKIP] [MA_TINH x 2 digits] [SBD_BAT_DAU x 4/6 digits] [SBD_KET_THUC x 4/6 digits] [DEBUG=T/F]')
	sys.exit()


TYPE = sys.argv[1]
MAX_SKIP = int(sys.argv[2])
MA_TINH = sys.argv[3]
SBD_BAT_DAU = sys.argv[4]
SBD_KET_THUC = sys.argv[5]
DEBUG = True if (sys.argv[6] == "T") else False
URL10 = "https://thanhnien.vn/giao-duc/tuyen-sinh/2018/tra-cuu-diem-thi-lop-10.html"
URL12 = "https://thanhnien.vn/giao-duc/tuyen-sinh/2018/tra-cuu-diem-thi-thpt-quoc-gia.html"
HEADER12 = "STT,Tinh,Ten,SBD,Nsinh,Gtinh,Toan,Van,Ly,Hoa,Sinh,KHTN,Su,Dia,GDCD,KHXH,NN,D12\n"
HEADER10 = "STT,Tinh,Ten,SBD,Nsinh,Gtinh,Van,NN,Toan,Chuyen,D5,D6,D7,D8,D9,D10,D11,D12,\Tong\n"
URL = URL10 if (TYPE == "10") else URL12
HEADER = HEADER10 if (TYPE == "10") else HEADER12


#####################################################################################
#																					#
#									Main Script										#
#																					#
#####################################################################################

if (DEBUG):
	print("Starting script ...")
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)
if (DEBUG):
	print("Loading Page ...")
driver.get(URL)

if (DEBUG):
	print("Reading Province Code ...")
p2c, c2p = readProvince("ma_tinh.txt")


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
	SBD = "%s%04d" % (MA_TINH,i)
	if (skips > MAX_SKIP):
		print("MAX_SKIP %d reached" % MAX_SKIP)
		break
	start_time = time.time()
	student = getStudent(getNext(SBD))
	if(DEBUG):
		print(student)
	if student is None:
		skips = skips + 1
	else:
		skips = 0
		writeResult(f, student)
	if (DEBUG):
		print("Done %s in %fs" % (SBD,time.time() - start_time))
print("Done ALL in %fs" % (time.time() - loop_time))

f.close()
driver.quit()
