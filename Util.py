# encode=utf-8

import json
import datetime
import threading
import logging
import inspect
import pymysql
import os

label_type = [
	'分类',
	'目标检测',
	'分割'
]
label_object = {
	'PaulinRaise': '篷布飘起',
	'Paulin': '篷布',
	'PaulinTorn': '篷布破损',
	'Fire': '火灾',
	'Leak': '货物撒漏',
	'Smoke': '烟雾',
	'PdoorOpen': '棚车车门开启',
	'PwindowOpen': '棚车车窗开启',
	'Kdoor': '客车车门',
	'Kwindow': '客车车窗',
	'CbdoorboltOpen': '敞车下门门栓开启',
	'Wheel': '车轮',
	'Object': '异物',
	'NoneObject': '非异物',
	'Person': '闲杂人员扒乘',
	'KbatterycapOpen': '客车电池箱盖开启',
	'Pipe': '风管',
	'Chain': '闸链',
	'AnglecockOpen': '折角塞门开启',
	'AnglecockClose': '折角塞门关闭',
	'GtankercapOpen': '罐车盖开启',
	'Steelcoil': '卷钢',
	'Tailcarriage': '尾车特征区',
	'Carriagejunction': '车厢连接处',
	'Cdoor': '敞车中门'
}
alarm_type = [
	'侧面车门',
	'侧面车窗',
	'侧面异物',
	'侧面动车注水口',
	'走行部尾部软管未吊起',
	'走行部闸链拉紧',
	'走行部折角塞门异常',
	'走行部软管连接异常',
	'走行部敞车下门门栓异常',
	'走行部尾车',
	'顶部异物',
	'顶部卷钢',
	'顶部盖开启',
	'顶部篷布破损'
]
cutting_relation = {
	'object': {
		'客车车门': ['K_DOOR_Cutting', ],
		'异物': ['J_OBJECT_Cutting', 'Joint_OBJECT_Cutting', 'T_OBJECT_Cutting'],
		'折角塞门开启': ['ZX_ANGLECOCK_Cutting', ],
		'折角塞门关闭': ['ZX_ANGLECOCK_Cutting', ],
		'闸链': ['ZX_CHAINPIPE_Cutting', ],
		'尾车特征区': ['ZX_CHAINPIPE_Cutting', ],
		'风管': ['ZX_CHAINPIPE_Cutting', ],
		'敞车下门门栓开启': ['ZX_C_BTMBOLT_Cutting', ]
	},
}
LOG = None
db = None
lock = threading.Lock()

HOST = ''
PORT = 0
DB_IP = ''
DB_PORT = 0
DB_USERNAME = ''
DB_USERPASSW0RD = ''
DB_NAME = ''
ROOT_DIR = ''

if os.path.exists('setting.json'):
	with open('setting.json', 'r') as fr:
		kd = json.load(fr)
		DB_IP = str(kd['db']['db_ip'])
		DB_PORT = int(kd['db']['db_port'])
		DB_USERNAME = str(kd['db']['db_username'])
		DB_USERPASSW0RD = str(kd['db']['db_password'])
		DB_NAME = str(kd['db']['db_name'])

		HOST = str(kd['server']['server_ip'])
		PORT = int(kd['server']['server_port'])
		ROOT_DIR = str(kd['server']['server_root'])

SYS_PATH = os.path.dirname(__file__)
if not os.path.exists(os.path.join(SYS_PATH, 'temp')):
	os.makedirs(os.path.join(SYS_PATH, 'temp'))
if not os.path.exists(os.path.join(SYS_PATH, 'temp', 'negative')):
	os.makedirs(os.path.join(SYS_PATH, 'temp', 'negative'))
if not os.path.exists(os.path.join(SYS_PATH, 'temp', 'replenish')):
	os.makedirs(os.path.join(SYS_PATH, 'temp', 'replenish'))
if not os.path.exists(os.path.join(SYS_PATH, 'temp', 'origin')):
	os.makedirs(os.path.join(SYS_PATH, 'temp', 'origin'))
if not os.path.exists(os.path.join(SYS_PATH, 'temp', 'glabel')):
	os.makedirs(os.path.join(SYS_PATH, 'temp', 'glabel'))
if not os.path.exists(os.path.join(SYS_PATH, 'temp', 'cutting')):
	os.makedirs(os.path.join(SYS_PATH, 'temp', 'cutting'))

NEGATIVE_DIR = os.path.normpath(os.path.join(SYS_PATH, 'temp', 'negative')) # 负样本暂存文件夹
REPLENISH_DIR = os.path.normpath(os.path.join(SYS_PATH, 'temp', 'replenish')) # 补充素材暂存文件夹
ORIGIN_DIR = os.path.normpath(os.path.join(SYS_PATH, 'temp', 'origin')) # 接收自服务器的原图
GLABEL_DIR = os.path.normpath(os.path.join(SYS_PATH, 'temp', 'glabel')) # 通过标注创建的分割标签
CUTTING_DIR = os.path.normpath(os.path.join(SYS_PATH, 'temp', 'cutting')) # 裁剪暂存文件夹


def _datetime_format(date=None, mode=None):
	if date is None:
		date = datetime.datetime.now()
	if mode == 1:
		return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日'
	elif mode == 2:
		return date.strftime('%Y%m%d%H%M%S')
	elif mode == 3:
		return date.strftime('%m/%d/%Y')
	elif mode == 4:
		return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日 ' + str(date.hour).zfill(
			2) + ':' + str(date.minute).zfill(2) + ':' + str(date.second).zfill(2)
	elif mode == 5:
		return date.strftime('%Y%m%d')


def _get_logger():
	logger = logging.getLogger('[数据管理平台]')
	this_file = inspect.getfile(inspect.currentframe())
	dirpath = os.path.abspath(os.path.dirname(this_file))
	if not os.path.exists(os.path.join(dirpath, 'log')):
		os.makedirs(os.path.join(dirpath, 'log'))
	handler = logging.FileHandler(os.path.join(dirpath, 'log', _datetime_format(mode=5) + ".log"))

	formatter = logging.Formatter(
		'[%(asctime)s][%(threadName)s:%(thread)d][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)
	return logger


if LOG is None:
	LOG = _get_logger()
	LOG.info('日志模块已载入')


def execute_sql(sql, args=None, need_commit=False):
	data = ()
	try:
		db = pymysql.connect(HOST, DB_USERNAME, DB_USERPASSW0RD, DB_NAME)
		cursor = db.cursor()
		if args is None:
			_affected_rows = cursor.execute(sql)
		else:
			_affected_rows = cursor.execute(sql, args=args)
		data = cursor.fetchall()
		if need_commit:
			db.commit()

	except Exception as e:
		db = None
		LOG.error(repr(e))
	finally:
		return data

def _create_default_label_table():
	for o in label_object.values():
		for t in label_type:
			_sql = 'insert into dmp.label (name, type) values(%s,%s);'
			execute_sql(_sql, args=(o, t), need_commit=True)

# if __name__ == '__main__':
# 	_create_default_label_table()
