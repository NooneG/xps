#-*- coding:utf-8 -*-
import random
import requests
import os
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from philips_jd.testcase.configuration_and_common_modules.configuration import *


class CommonModules:
    global URLLIST

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(18)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        print("Start")

    def tearDown(self):
        print('End')

    def img(self):
        """在指定目录下，保存截图文件"""
        PATH = lambda p: os.path.abspath(p)
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        timestamp_1 = time.strftime('%Y-%m-%d')
        path = PATH("./testcase/report/" + timestamp_1 + "/screenshot")
        name = PATH(path + "\\" + timestamp + ".png")
        if not os.path.isdir(PATH("D:/ROOM" + "/" +timestamp_1 + "/screenshot")):
            os.makedirs(path)
        self.driver.get_screenshot_as_file(name)
        print('screenshot:', timestamp, '.png')

    def edi_generate_sales_order(self):
        """
        通过edi模拟工具，修改数据库数据，再导入系统生成销售订单
        :return:
        """
        url = 'http://47.104.154.165:20020/edi/list?pageSize=60&pageNumber=1&projectId=&startTime=&ednTime=&purchaseNo=&salesOrderNo=&importType=1&importStatus=2'
        get_result1 = requests.get(url) ## 获取符合未导入的采购订单
        logger.info('get_result1 %s', get_result1)

        data = get_result1.json() ## 返回的Json，并解析
        list = data['data']['list']
        for t in list:
            id = t['id']
            purchaseNo = t['purchaseNo']
            logger.info('id %s,purchaseNo %s', id, purchaseNo)

            ## EDI模拟工具，修改数据库对应数据
            url_sale = 'http://47.104.154.165:11080/edi/util/putPurchase2'
            self.Order = random.randint(1000000000, 9999999999)
            json = """{"purchaseOrderDetails":[{"backorderProcessing":"","buyerProductId":"%s","comments":"","costPrice":"254.15","currentRecordNumber":1,"dataLable":"Order","discount":"0.0","documentNumber":"%s","listPrice":"","productCode":"%s","productName":"飞利浦（PHILIPS）儿童理发器礼品套装HC1099/15BP婴儿剃头刀可水洗电推子低噪音电推剪配安抚奶嘴","quantity":40,"vendorProductId":"%s"}],"purchaseOrderSummary":{"arrived":"","buyerGLN":"6907777414174","comments":"","dataLable":"Order Catalogue","departmentCode":"P008","distributionCenter":"深圳","distributionCenterID":"603","documentNumber":"%s","documentRecordCount":1,"orderAttribute":"(A)自动补货","orderType":"","ouCode":"81","prePurchaseCode":"","purchaseContact":"丁海晨","purchaseDate":"2018-10-24 05:56:10","purchasedBy":"%s","receiver":"黄荣峰","receiverTel":"4006225686转02034,13760174117","receivingAddress":"惠州市惠阳区经济开发区三和大道嘉民产业园207门口","requiredArrivalDate":"2018-10-24 05:56:10","totalAmount":"","totalCategory":1,"totalCostAmount":"10166.0","totalQuantity":40,"vendorGLN":"","warehouse":"商超A休闲食品仓1号库","warehouseGLN":"6971416330408","warehouseId":"0"},"transferSubject":{"buyerName":"京东商城","comments":"","dataGenerationDate":"2018-10-24 05:56:10","dataLable":"Header","dataReceiver":"深圳越海全球供应链有限公司","dataSender":"京东","documentType":"PURCHASEORDER","transferFileId":"京东_深圳越海全球供应链有限公司_采购_66765028","transferLable":"首次","transferRecordCount":"3","vendorId":"szyh","vendorName":"深圳越海全球供应链有限公司"}}""" % (
                '5823429', self.Order, '5823429', '5823429', self.Order, self.Order)
            post_result = requests.post(url_sale, data=[("id", id), ("json", json), ("purchaseNo", self.Order)])
            logging.info('post_result %s', post_result.text)

            get_result = requests.get('http://47.104.154.165:20020/edi/call?id={id}&type=1'.format(id= id))
            logger.info('get_result %s', get_result.text)
            break

    def edi_sales_order_receipt(self):
        """
        通过edi模拟工具，修改数据库数据，再导入发货确认单
        :return:
        """
        ## 查询未导入状态的，收货确认单
        url = 'http://47.104.154.165:20020/edi/list?pageSize=60&pageNumber=1&projectId=&startTime=&ednTime=&purchaseNo=&salesOrderNo=&importType=4&importStatus=2'
        get_result1 = requests.get(url)  ## 获取符合未导入的采购订单
        logger.info('get_result1 %s', get_result1)

        data = get_result1.json()  ## 返回的Json，并解析
        list = data['data']['list']
        for t in list:
            id = t['id']
            purchaseNo = t['purchaseNo']
            logger.info('id %s,purchaseNo %s', id, purchaseNo)

            url_signing = 'http://47.104.154.165:20020/edi/util/putConfirm'
            json = '''[{"count":"2","productCode":"1356504"}]'''
            post_signing_result = requests.post(url_signing,
                                                data=[("id", id), ("salesOrderNo", self.sales_order_number), ("json", json)])
            logger.info('post_signing_result %s', post_signing_result.text)

            get_result = requests.get('http://47.104.154.165:20020/edi/call?id={id}&type=4'.format(id=id))
            break

    def edi_main_item_return(self):
        """
        通过edi模拟工具，创建主件退货单
        :param purchaseNo:
        :return:
        """
        url = 'http://47.104.154.165:20020/edi/list?pageSize=60&pageNumber=1&projectId=&startTime=&ednTime=&purchaseNo=&salesOrderNo=&importType=5&importStatus=2'
        get_result1 = requests.get(url) ## 获取未导入的主件退货单
        logger.info('get_result1 %s', get_result1)
        data = get_result1.json()
        list = data['data']['list']
        for t in list:
            id = t['id']
            purchaseNo = t['purchaseNo']
            logger.info('retrunNo %s,id %s', purchaseNo, id)

            get_result = requests.get(
                'http://47.104.154.165:16020/edi/util/putSpare?id={id}&jdSkuCode=8081739&projectId=146798165'.format(
                    id=id))
            logger.info('get_result %s', get_result.text)

            self.driver.get(URLLIST['url_order_management'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#order-management > div.sales-management-table.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )

            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                order_status = self.driver.find_element_by_xpath(
                    '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[5]/div'.format(
                        sort=t + 1)).text
                sales_order_number = self.driver.find_element_by_xpath(
                    '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[3]/div'.format(
                        sort=t + 1)).text
                logger.info('order_status %s,sales_order_number %s', order_status, sales_order_number)

                if order_status == '已签收':
                    ## 修改指定edi单号下的信息  id：edi主键id值 json：修改edi的JSON数据
                    url_sale = 'http://47.104.154.165:16020/edi/util/putMain'
                    json = """ [{"count":"5","purchaseNo":"%s","jdSkuCode":"5115396","price":"200.00"}]""" % (
                        sales_order_number)
                    logger.info("json %s", json)
                    post_result = requests.post(url_sale, data=[("id", id), ("json", json)])
                    logging.info('post_result %s', post_result.text)

                    ## 将修改的edi导入系统，完成销售退货订单
                    get_result = requests.get('http://47.104.154.165:16020/edi/call?id={id}&type=5'.format(id=id))
                    logger.info('get_result %s', get_result.text)
                    break
            break

    def edi_spare_parts_return(self):
        """
        通过edi模拟工具，创建备件退货单
        :return:
        """
        url = 'http://47.104.154.165:20020/sales/spare/list?returnNo=&startTime=&endDate=&status=&spareStatus=3&jdSkuCode=&pageNumber=1&pageSize=60'
        get_result1 = requests.get(url)  ## 获取符合备件退货的单号
        logger.info('get_result1 %s', get_result1)

        data = get_result1.json()  ## 返回的Json，并解析
        list = data['data']['list']
        for t in list:
            id = t['id']
            returnNo = t['returnNo']
            jdSkuCode = t['jdSkuCode']
            logger.info('retrunNo %s,id %s,jdSkuCode %s', returnNo, id, jdSkuCode)

            ## EDI模拟工具，修改数据库对应数据
            get_result = requests.get(
                'http://47.104.154.165:11080/edi/util/putSpare?id={id}&jdSkuCode=5823429&projectId=146798171'.format(
                    id=id))
            logger.info('get_result %s', get_result.text)

            self.driver.get('http://47.104.154.165:20020/philips/jd/fenxiao/main/#/AfterSalesManagement')

            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="after-sales-management"]/div[1]/form/div[1]/div[2]/div/div/input'))
            )
            self.driver.find_element_by_xpath(
                '//*[@id="after-sales-management"]/div[1]/form/div[2]/div[3]/div/div/textarea').send_keys(
                returnNo)
            self.driver.find_element_by_css_selector(
                '#after-sales-management > div.after-sales-management-form.fx-theme-form > form > div:nth-child(3) > div.el-form-item.fx-theme-search.el-form-item--small > div > button > span').click()
            sleep(2)

            table_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//*[@id="after-sales-management"]/div[3]/div/div[3]/table/tbody'))
            )

            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                new_jdSkuCode = self.driver.find_element_by_xpath(
                    '//*[@id="after-sales-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                new_returnNo = self.driver.find_element_by_xpath(
                    '//*[@id="after-sales-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[3]/div'.format(
                        sort=t + 1)).text
                logger.info('new_jdSkuCode %s,new_returnNo %s', new_jdSkuCode, new_returnNo)

                if new_jdSkuCode == jdSkuCode and new_returnNo == returnNo:
                    self.driver.find_element_by_xpath(
                        '//*[@id="after-sales-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/label/span/span'.format(
                            sort=t + 1)).click()

                    sleep(0.5)
                    self.driver.find_element_by_xpath(
                        '//*[@id="after-sales-management"]/div[2]/div/button[2]/span').click()
                    logger.info('ok')
                    sleep(5)
                    break
            break

    def wms_simulation_library_feedback(self,outbound_order_number):
        """
        操作wms模拟工具，进行出库信息反馈
        :param outbound_order_number: 出库通知单号
        :return:
        """
        i = 0
        self.driver.get(URLLIST['url_simulate_WMS'])
        while i < 14:  ## 循环14次，每次间隔5s
            ## 点击“出库通知单”按钮
            self.driver.find_element_by_css_selector("#simulate-wms > div > div.fx-button > button.el-button.el-button--success.el-button--small").click()
            sleep(2)

            table_row_list = self.driver.find_element_by_xpath( ## 获取wms模拟的出库单表格
                '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody').find_elements_by_tag_name('tr')
            logger.info("Get the form successfully")
            for t, tr in enumerate(table_row_list): ## 遍历表格内容
                new_outbound_order_number = self.driver.find_element_by_xpath(  ## 获取wms模拟的出库单号
                    '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(
                        sort=t + 1)).text
                if new_outbound_order_number == outbound_order_number:
                    self.driver.find_element_by_xpath(  ## 点击“反馈信息”按钮
                        '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody/tr[{sort}]/td[7]/div/button/span'.format(
                            sort=t + 1)).click()
                    i=14
                    logger.info("Successful wms_simulation_library_feedback")
                    break
                elif t > 5:
                    break
            i += 1
            self.driver.refresh() ## 刷新页面
            sleep(2)

    def wms_simulation_feedback_storage(self,inbound_order_number):
        """
        操作wms模拟工具，进行入库信息反馈
        :param inbound_order_number: 入库通知单号
        :return:
        """
        i = 0
        self.driver.get(URLLIST['url_simulate_WMS'])
        while i < 14:  ## 循环14次，每次间隔5s
            sleep(3)
            table_row_list = self.driver.find_element_by_xpath( ## 获取wms模拟的入库单表格
                '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody').find_elements_by_tag_name('tr')
            logger.info("frequency %s Get the form successfully",i+1)
            for t, tr in enumerate(table_row_list): ## 遍历表格内容
                new_inbound_order_number = self.driver.find_element_by_xpath( ## 获取wms模拟的入库单号
                    '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(sort=t + 1)).text
                if new_inbound_order_number == inbound_order_number:
                    logger.info('ok')
                    self.driver.find_element_by_xpath( ## 点击“反馈信息”按钮
                        '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody/tr[{sort}]/td[7]/div/button/span'.format(
                            sort=t + 1)).click()
                    sleep(2)
                    i=14
                    logger.info("Successful wms_simulation_feedback_storage")
                    break
                elif t >6:
                    break
            i += 1
            sleep(2)
            self.driver.refresh() ## 刷新页面
