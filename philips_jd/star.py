#-*- coding:utf-8 -*-
import os
import time
import unittest
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from philips_jd.testcase.bizflow.purchase_flow import PurchaseFlow
from philips_jd.testcase.bizflow.sales_flow import SalesFlow
from common_lib.HTMLTestRunner import HTMLTestRunner

def report(name):
	"""
	用测试报告的方式运行测试用例
	:param name:项目名称
	:return:
	"""
	## """创建文件夹"""
	path = lambda p: os.path.abspath(p)
	timestamp = time.strftime('%Y-%m-%d')
	filepath = path('./testcase/report/' + timestamp)
	filename = filepath + "\\" + timestamp + name + '.html'
	if not os.path.isdir(filepath):
		os.makedirs(filepath)

	## """运行指定测试用例，并在指定目录下，创建报告"""
	# discover = unittest.defaultTestLoader.discover(test_path, pattern="test*.py")
	suite = unittest.TestSuite()
	tests = [PurchaseFlow('test_success_procurement'),  ## 采购流程，直到交易完成
			 PurchaseFlow('test_same_product_exchange'),  ## 采购同品换货，直到换货完成
			 PurchaseFlow('test_foreign_exchange'),  ## 采购异品换货，直到换货完成

			 SalesFlow('test_successful_sales'),  ## 销售流程，直到已签收
			 SalesFlow('test_main_item_sales_return'),  ## 主件退货流程，直到退货完成
			 SalesFlow('test_spare_parts_return')  ## 备件退货流程，直到脱货完成
			 ]
	suite.addTests(tests)
	with open(file=filename, mode="wb") as f:
		runner = HTMLTestRunner(stream=f, title=u"飞利浦分销项目测试报告", description=u"测试用例执行情况")
		runner.run(suite)


report('PHFX')

# print(sys.path)