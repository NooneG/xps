#-*- coding:utf-8 -*-
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from tenacity import retry,stop_after_attempt
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry,stop_after_attempt,wait_random
import unittest
import logging
import requests

from philips_jd.testcase.configuration_and_common_modules.configuration import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SalesReturnFlow(unittest.TestCase):
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

    def wms_simulation_library_feedback(self,outbound_order_number):
        """
        操作wms模拟工具，进行出库信息反馈
        :param outbound_order_number: 出库通知单号
        :return:
        """
        i = 0
        url = "http://47.104.154.165:58008/simulate/main/wms/index.html#/SimulateWMS"
        self.driver.get(url)
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
        url = "http://47.104.154.165:58008/simulate/main/wms/index.html#/SimulateWMS"
        self.driver.get(url)
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
                        '//*[@id="simulate-wms"]/div/div[2]/div/div[3]/table/tbody/tr[{sort}]/td[7]/div/button/span'.format(sort=t + 1)).click()
                    sleep(2)
                    i=14
                    logger.info("Successful wms_simulation_feedback_storage")
                    break
                elif t >6:
                    break
            i += 1
            sleep(2)
            self.driver.refresh() ## 刷新页面

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3))
    def test_spare_parts_return(self):
        """测试备件退货流程，直到退货完成"""
        self.edi_spare_parts_return()

        self.driver.get(URLLIST['url_sales_returns_management'])
        table_element = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "#sales-return-management > div.sales-management-table.fx-theme-table"))
        )

        table_row_list = table_element.find_elements_by_tag_name('tr')
        logger.info('Successful table_row_list')
        for t, tr in enumerate(table_row_list):  ## 遍历表格内容
            order_status = self.driver.find_element_by_xpath(
                '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                    sort=t + 1)).text
            return_type = self.driver.find_element_by_xpath(
                '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[5]/div'.format(
                    sort=t + 1)).text

            if order_status == '创建' and return_type == '售后退货':
                sales_return_order = self.driver.find_element_by_xpath(  ## 获取，销售退货单单号
                    '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                self.driver.find_element_by_xpath(  ## 点击可“编辑”的销售退货单
                    '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[12]/div/button/span'.format(
                        sort=t + 1)).click()

                ## 选择收货人地址
                receiving_city = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                '#city-picker-template > span'))
                )
                receiving_city.click()
                city = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                '#city-picker-template > div > div > div.region-select-content > div.region-select.province > dl:nth-child(1) > dd > a:nth-child(6)'))
                )
                city.click()

                ## 选择退货仓库
                self.driver.find_element_by_css_selector(
                    '#sales-return-edit > div.customer-info > form > div > div:nth-child(2) > div.el-form-item.is-error.is-required.el-form-item--small > div > div.el-select.el-select--small > div > input').click()
                ActionChains(self.driver).move_to_element(
                    self.driver.find_element_by_css_selector(
                        "body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap")).perform()
                self.driver.find_element_by_css_selector(
                    'body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li.el-select-dropdown__item.hover').click()

                ## 输入详细地址
                ActionChains(self.driver).move_to_element(
                    self.driver.find_element_by_css_selector(
                        '#sales-return-edit > div.customer-info > form > div > div:nth-child(3) > div:nth-child(1) > div')).perform()
                self.driver.find_element_by_xpath(
                    '//*[@id="sales-return-edit"]/div[2]/form/div/div[3]/div[1]/div/div[1]/input').send_keys(
                    '惠州市惠阳区经济开发区三和大道嘉民产业园207门口')

                ## 输入手机号
                ActionChains(self.driver).move_to_element(
                    self.driver.find_element_by_css_selector(
                        "#sales-return-edit > div.customer-info > form > div > div:nth-child(4) > div.el-form-item.yh-required.el-form-item--small > div")).perform()
                self.driver.find_element_by_xpath(
                    '//*[@id="sales-return-edit"]/div[2]/form/div/div[4]/div[1]/div/div/input').send_keys(
                    '4006225686转02034,13760174117')

                ## 点击保存并提交
                self.driver.find_element_by_css_selector(
                    '#sales-return-edit > div.fx-button > button.el-button.el-button--primary.el-button--small > span').click()
                break

        sleep(2)

        ## 通过入库单查询页面，查询对应的入库单号(wms模拟工具需要入库单号判断)
        self.driver.get(URLLIST['url_warehousing_notice'])

        ## 获取对应的入库单号，inbound_order_number
        ActionChains(self.driver).move_to_element(
            self.driver.find_element_by_xpath(
                '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div')).perform()
        inbound_order_number = self.driver.find_element_by_xpath(
            '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[1]/td[1]/div/a').text
        logger.info('inbound_order_number %s', inbound_order_number)

        self.wms_simulation_feedback_storage(inbound_order_number)

        sleep(30)  ## 等待程序处理

        self.driver.get(URLLIST['url_sales_returns_management'])
        self.driver.find_element_by_xpath(
            '//*[@id="sales-return-management"]/div[1]/form/div[1]/div[2]/div/div/input').send_keys(sales_return_order)
        self.driver.find_element_by_css_selector(
            '#sales-return-management > div.sales-return-management-form.fx-theme-form > form > div:nth-child(2) > div.el-form-item.fx-theme-search.el-form-item--small > div > button').click()

        return_status = self.driver.find_element_by_xpath(
            '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[1]/td[4]/div').text

        self.assertEqual(return_status, '退货完成', '测试成功')


    def edi_main_item_return(self):
        """
        通过edi模拟工具，创建主件退货单
        :param purchaseNo:
        :return:
        """
        url = 'http://47.104.154.165:16020/edi/list?pageSize=60&pageNumber=1&projectId=&startTime=&ednTime=&purchaseNo=&salesOrderNo=&importType=5&importStatus=2'
        get_result1 = requests.get(url)
        logger.info('get_result1 %s', get_result1)
        data = get_result1.json()
        list = data['data']['list']
        for t in list:
            id = t['id']
            purchaseNo = t['purchaseNo']
            logger.info('retrunNo %s,id %s', purchaseNo, id)
            break

        get_result = requests.get(
            'http://47.104.154.165:11080/edi/util/putSpare?id={id}&jdSkuCode=8081739&projectId=146798165'.format(
                id=id))
        logger.info('get_result %s', get_result.text)

        self.driver.get('http://47.104.154.165:16020/philips/jd/gehu/main/#/OrderManagement')

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

    def xx(self):
        self.edi_main_item_return()

if __name__ == '__main__':
    unittest.main()
