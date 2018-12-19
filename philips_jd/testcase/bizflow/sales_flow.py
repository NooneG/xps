#-*- coding:utf-8 -*-
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry,stop_after_attempt,wait_random
import unittest
import logging
import pymysql

from philips_jd.testcase.configuration_and_common_modules.configuration import *
from philips_jd.testcase.configuration_and_common_modules.common_modules import CommonModules


class SalesFlow(CommonModules,unittest.TestCase):

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3))
    def test_successful_sales(self):
        """
        测试销售流程，直到销售订单已签收
        :return:
        """
        try:
            self.edi_generate_sales_order() ## 通过edi模拟工具生成销售订单
            self.driver.get(URLLIST['url_order_management']) ## 进入订单管理页面

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#order-management > div.sales-management-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )

            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            customer_order_number = str(self.Order)
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                new_customer_order_number = self.driver.find_element_by_xpath(  ## 获取订单管理页面的“客户单号”字段数据
                    '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[3]/div'.format(
                        sort=t + 1)).text

                if new_customer_order_number == customer_order_number:
                    self.sales_order_number = self.driver.find_element_by_xpath(  ## 获取销售单号
                        '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                            sort=t + 1)).text
                    self.driver.find_element_by_xpath(  ## 点击“发货通知”按钮
                        '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[15]/div/button'.format(
                            sort=t + 1)).click()

                    ## 选择收货城市
                    receiving_city = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    '#city-picker-template > span > div'))
                    )
                    receiving_city.click()
                    self.driver.find_element_by_css_selector( ## 选择省份
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.province > dl:nth-child(1) > dd > a:nth-child(6)').click()
                    self.driver.find_element_by_css_selector( ## 选择城市
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.city > dl > dd > a:nth-child(11)').click()
                    self.driver.find_element_by_css_selector( ## 选择县区
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.district > dl > dd > a:nth-child(2)').click()

                    ## 选择要求发货日期
                    self.driver.find_element_by_css_selector(
                        '#order-delivery > div.order-delivery-form > form > div:nth-child(1) > div:nth-child(2) > div > div > input').click()
                    ActionChains(self.driver).move_to_element(self.driver.find_element_by_css_selector(
                        'body > div.el-picker-panel.el-date-picker.el-popper > div.el-picker-panel__body-wrapper > div')).perform()
                    self.driver.find_element_by_css_selector(
                        'td.available.today > div > span').click()

                    ## 选择送货方式
                    self.driver.find_element_by_css_selector(
                        '#order-delivery > div.order-delivery-form > form > div:nth-child(1) > div:nth-child(3) > div > div > div.el-input.el-input--small.el-input--suffix > span').click()
                    ActionChains(self.driver).move_to_element(self.driver.find_element_by_css_selector(
                        "body > div.el-select-dropdown.el-popper > div.el-scrollbar")).perform()
                    self.driver.find_element_by_css_selector(
                        'body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li.el-select-dropdown__item.hover').click()

                    ## 选择批次
                    self.driver.find_element_by_xpath(
                        '//*[@id="order-delivery"]/div[2]/div/div[3]/table/tbody/tr[1]/td[4]/div/button/span').click()
                    self.driver.find_element_by_xpath(
                        '//*[@id="order-delivery"]/div[3]/div/div[2]/div[1]/div[3]/table/tbody/tr[1]/td[7]/div/button/span').click()

                    ## 输入本次预约数量
                    required_quantity = self.driver.find_element_by_css_selector(
                        '#order-delivery > div.order-delivery-table > h4 > b:nth-child(4)').text
                    number_of_reservations = self.driver.find_element_by_xpath(
                        '//*[@id="order-delivery"]/div[2]/div/div[3]/table/tbody/tr[1]/td[7]/div/div/input')
                    number_of_reservations.clear()
                    number_of_reservations.send_keys(required_quantity)

                    ## 点击“提交”按钮
                    self.driver.find_element_by_css_selector(
                        '#order-delivery > div.fx-button.fx-button-center > button.el-button.el-button--primary.el-button--small').click()
                    sleep(1)
                    break

            ## 出库通知单页面，获取销售订单对应的出库单
            self.driver.get(URLLIST['url_outgoing_notice'])
            input_sales_order_number = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="outgoing-notice"]/div[1]/form/div[2]/div[1]/div/div/input'))
            )
            input_sales_order_number.send_keys(self.sales_order_number)
            self.driver.find_element_by_css_selector(
                'div.el-form-item.fx-theme-search.el-form-item--small > div > button').click()
            sleep(2)
            outbound_order_number = self.driver.find_element_by_xpath(
                '//*[@id="outgoing-notice"]/div[3]/div/div[3]/table/tbody/tr[1]/td[1]/div/a').text

            self.wms_simulation_library_feedback(outbound_order_number)
            self.edi_sales_order_receipt()

            sleep(10)

            ## 查询销售订单的状态
            self.driver.get(URLLIST['url_order_management'])

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#order-management > div.order-management-form > form > div:nth-child(1) > div > div > input"))
            )

            self.driver.find_element_by_css_selector(
                '#order-management > div.order-management-form > form > div:nth-child(1) > div > div > input').send_keys(self.sales_order_number)
            self.driver.find_element_by_css_selector(
                '#order-management > div.order-management-form.fx-theme-form > form > div.el-form-item.fx-theme-search.el-form-item--small > div > button').click()
            sale_order = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr/td[5]/div'))
            )

            sale_order_status = sale_order.text
            self.assertEqual(sale_order_status,'已签收','测试销售签收流程成功')
        except:
            self.img()
            raise

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3))
    def test_main_item_sales_return(self):
        """
        测试主件退货流程，直到退货完成
        :return:
        """
        try:
            self.driver.get(URLLIST['url_order_management'])  ## 进入订单管理页面
            sleep(1)

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )

            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                sales_status = self.driver.find_element_by_xpath(
                    '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[5]/div'.format(
                        sort=t+1)).text
                if sales_status == '已签收':
                    self.sales_order_number = self.driver.find_element_by_xpath(  ## 获取订单管理页面的“销售单号”字段数据
                        '//*[@id="order-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[3]/div'.format(
                            sort=t + 1)).text
                    break

            self.edi_main_item_return() ## 通过edi模拟工具，创建主件退货单

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

                if order_status == '创建' and return_type == '销售退货':
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

                    self.driver.find_element_by_css_selector(  ## 选择城市
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.city > dl > dd > a:nth-child(11)').click()
                    self.driver.find_element_by_css_selector(  ## 选择县区
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.district > dl > dd > a:nth-child(2)').click()

                    ## 选择退货仓库
                    self.driver.find_element_by_css_selector(
                        'div.el-form-item.is-error.is-required.el-form-item--small > div > div.el-select.el-select--small > div.el-input.el-input--small.el-input--suffix > input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[1]/ul/li[2]').click()

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

                    ## 点击保存并提交
                    self.driver.find_element_by_xpath(
                        '//*[@id="sales-return-edit"]/div[3]/button[1]').click()
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
            logger.info('inbound_order_number %s',inbound_order_number)

            self.wms_simulation_feedback_storage(inbound_order_number)

            sleep(30) ## 等待程序处理

            self.driver.get(URLLIST['url_sales_returns_management'])
            self.driver.find_element_by_xpath(
                '//*[@id="sales-return-management"]/div[1]/form/div[1]/div[2]/div/div/input').send_keys(sales_return_order)
            self.driver.find_element_by_css_selector(
                '#sales-return-management > div.sales-return-management-form.fx-theme-form > form > div:nth-child(2) > div.el-form-item.fx-theme-search.el-form-item--small > div > button').click()

            return_status = self.driver.find_element_by_xpath(
                '//*[@id="sales-return-management"]/div[3]/div/div[3]/table/tbody/tr[1]/td[4]/div').text

            self.assertEqual(return_status,'退货完成','测试成功')
        except:
            self.img()
            raise

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3))
    def test_spare_parts_return(self):
        """
        测试备件退货流程，直到退货完成
        :return:
        """
        try:
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
        except:
            self.img()
            raise 

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    tests = [#SalesFlow('test_successful_sales'),  ## 销售流程，直到已签收
             # SalesFlow('test_main_item_sales_return'),  ## 主件退货流程，直到退货完成
             SalesFlow('test_spare_parts_return')  ## 备件退货流程，直到脱货完成
             ]
    suite.addTests(tests)
    runer = unittest.TextTestRunner()
    runer.run(suite)

    # x=SalesFlow()
    # x.test_successful_sales()