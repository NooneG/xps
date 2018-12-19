#-*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry,stop_after_attempt,wait_random,before_sleep_log
from time import sleep
import unittest
import logging

from philips_jd.testcase.configuration_and_common_modules.configuration import *
from philips_jd.testcase.configuration_and_common_modules.common_modules import CommonModules


class PurchaseFlow(CommonModules,unittest.TestCase):

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3),before_sleep=before_sleep_log(logger, logging.DEBUG))
    def test_success_procurement(self):
        """
        测试采购流程，直到交易成功
        :return:
        """
        try:
            ## 找到可“编辑”的采购订单
            self.driver.get(URLLIST['url_purchase_order_management'])
            purchase_order_table_row_list = self.driver.find_element_by_css_selector(
                '#purchase-management > div.purchase-management-table > div > div.el-table__fixed-right > div.el-table__fixed-body-wrapper > table > tbody'
                ).find_elements_by_tag_name("tr")

            for t, tr in enumerate(purchase_order_table_row_list):
                if "编辑" == tr.text:
                    ## 记录可“编辑”的采购订单订单号，进入“编辑采购单”页面
                    purchase_order_number = self.driver.find_element_by_xpath('//*[@id="purchase-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/a'.format(sort = t+1)).text
                    logger.info('Purchase Order No %s',purchase_order_number)
                    self.driver.find_element_by_xpath(
                        '//*[@id="purchase-management"]/div[3]/div/div[4]/div[2]/table/tbody/tr[{sort}]/td[11]/div/button[1]/span'.format(sort = t+1)).click()

                    ## 选择供应商，飞利浦（中国）投资有限公司
                    self.driver.find_element_by_css_selector(
                        '#purchase-order-edit > div.purchase-order-edit-form > form > div > div:nth-child(1) > div:nth-child(1) > div > div > div.el-input.el-input--small.el-input--suffix > input').click()
                    supplier = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    "body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li"))
                    )
                    supplier.click()

                    ## 选择仓库，苏州望亭仓
                    self.driver.find_element_by_css_selector(
                        '#purchase-order-edit > div.purchase-order-edit-form > form > div > div:nth-child(1) > div:nth-child(2) > div > div > div.el-input.el-input--small.el-input--suffix > input').click()
                    ActionChains(self.driver).move_to_element(self.driver.find_element_by_css_selector("body > div:nth-child(6)")).perform()
                    self.driver.find_element_by_css_selector(
                        "body > div:nth-child(6) > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li.el-select-dropdown__item.hover").click()

                    ## 选择供应商是否开票，是
                    self.driver.find_element_by_css_selector(
                        '#purchase-order-edit > div.purchase-order-edit-form > form > div > div:nth-child(3) > div:nth-child(1) > div > div > div.el-input.el-input--small.el-input--suffix > input').click()
                    ActionChains(self.driver).move_to_element(self.driver.find_element_by_css_selector("body > div:nth-child(7)")).perform()
                    self.driver.find_element_by_css_selector(
                        "body > div:nth-child(7) > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap > ul > li.el-select-dropdown__item.hover").click()

                    ## 选择要求到货时间，测试当天
                    self.driver.find_element_by_css_selector(
                        '#purchase-order-edit > div.purchase-order-edit-form > form > div > div:nth-child(4) > div.el-form-item.yh-required.el-form-item--small > div > div > input').click()
                    request_arrival_time = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    "td.available.today > div > span"))
                    )
                    request_arrival_time.click()

                    ## 点击“保存并提交”按钮
                    self.driver.find_element_by_css_selector(
                        "button.el-button.el-button--primary.el-button--small > span").click()
                    logger.info('Purchase order editing completed')
                    break

            sleep(2)

            ## 查询对应的采购订单
            self.driver.find_element_by_css_selector(
                '#purchase-management > div.purchase-management-form.fx-theme-form > form > div:nth-child(1) > div:nth-child(1) > div > div > input').send_keys(
                purchase_order_number)
            self.driver.find_element_by_css_selector(
                '#purchase-management > div.purchase-management-form.fx-theme-form > form > div:nth-child(2) > div.el-form-item.fx-theme-search.el-form-item--small > div > button > i').click()
            sleep(1)

            ## 采购订单预约入库
            reserve_warehousing = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="purchase-management"]/div[3]/div/div[4]/div[2]/table/tbody/tr[1]/td[11]/div/button/span'))
            )
            reserve_warehousing.click()
            sleep(2)
            self.driver.find_element_by_css_selector('#purchase-in-storage > div.fx-button.fx-button-center > button.el-button.el-button--primary.el-button--small > span').click()
            sleep(1)
            logger.info('Appointment to the warehouse successfully')

            ## 通过入库单查询页面，查询对应的入库单号(wms模拟工具需要入库单号判断)
            self.driver.get(URLLIST['url_warehousing_notice'])
            sleep(1)
            self.driver.find_element_by_css_selector( ## 输入采购单号
                'form > div.el-row > div:nth-child(2) > div > div > input').send_keys(
                purchase_order_number)
            self.driver.find_element_by_css_selector( ## 开始查询
                'div.el-form-item.fx-theme-search.el-form-item--small > div > button > span').click()

            ## 获取对应的入库单号，inbound_order_number
            ActionChains(self.driver).move_to_element(
                self.driver.find_element_by_css_selector(
                    "div > div.el-table__body-wrapper.is-scrolling-none > table")).perform()
            inbound_order_number = self.driver.find_element_by_xpath(
                '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[1]/td[1]/div/a').text
            logger.info('Query the inbound order number successfully %s', inbound_order_number)

            ## 通过模拟wms页面，模拟反馈信息
            self.wms_simulation_feedback_storage(inbound_order_number)

            ## 预留时间给系统处理，反馈的信息
            sleep(30)

            ## 返回采购管理页面，采购订单状态为“交易成功”
            self.driver.get(URLLIST['url_purchase_order_management'])
            self.driver.find_element_by_css_selector(
                'div:nth-child(1) > div:nth-child(1) > div > div > input').send_keys(
                purchase_order_number)
            self.driver.find_element_by_css_selector(
                'div:nth-child(2) > div.el-form-item.fx-theme-search.el-form-item--small > div > button > i').click()
            sleep(1)

            purchase_order_status = self.driver.find_element_by_xpath(
                '//*[@id="purchase-management"]/div[3]/div/div[3]/table/tbody/tr/td[7]/div').text
            self.assertEqual(purchase_order_status,'交易成功',"测试采购交易流程成功")
        except:
            self.img()
            raise 

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3),before_sleep=before_sleep_log(logger, logging.DEBUG))
    def test_same_product_exchange(self):
        """
        测试同品换货，直到换货成功
        :return:
        """
        try:
            self.driver.get(URLLIST['url_inventory_warehouse'])

            sleep(0.5)
            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#inventory-warehouse > div.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                new_quantity = self.driver.find_element_by_xpath( ## 数量字段
                    '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[8]/div'.format(
                        sort=t + 1)).text
                new_warehouse_name = self.driver.find_element_by_xpath( ## 仓库名称字段
                    '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                        sort=t + 1)).text
                logger.info('new_quantity %s,new_warehouse_name %s', new_quantity, new_warehouse_name)

                if new_quantity != 0: ## 如果库存数量不为0，则创建换货单
                    self.driver.find_element_by_xpath( ## 点击小框框
                        '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/label/span/span'.format(
                            sort=t + 1)).click()

                    sleep(0.5)

                    self.driver.find_element_by_css_selector( ## 创建同品换货单
                        '#inventory-warehouse > div.fx-theme-button > div > button:nth-child(2) > span').click()

                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[12]/div/div/input'))
                    )
                    self.driver.find_element_by_xpath(  ## 输入退货数量
                        '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[12]/div/div/input').send_keys(
                        '2')

                    self.driver.find_element_by_xpath(  ## 输入收货人
                        '//*[@id="purchase-create-identical"]/div[2]/form/div[1]/div[2]/div/div[1]/input').send_keys(
                        '吴平')

                    self.driver.find_element_by_css_selector(  ## 选择收货人地址
                        '#city-picker-template > span').click()
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    "#city-picker-template > div"))
                    )
                    self.driver.find_element_by_css_selector(  ## 选择省份
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.province > dl:nth-child(1) > dd > a:nth-child(6)').click()
                    self.driver.find_element_by_css_selector(  ## 选择城市
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.city > dl > dd > a:nth-child(11)').click()
                    self.driver.find_element_by_css_selector(  ## 选择县区
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.district > dl > dd > a:nth-child(2)').click()

                    self.driver.find_element_by_xpath(  ## 输入详细地址
                        '//*[@id="purchase-create-identical"]/div[2]/form/div[2]/div[1]/div/div[1]/input').send_keys(
                        '惠州市惠阳区经济开发区三和大道嘉民产业园207门口')

                    self.driver.find_element_by_xpath(  ## 选择是否开票:否
                        '//*[@id="purchase-create-identical"]/div[3]/form/div[1]/div[1]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[1]/ul/li[2]').click()

                    self.driver.find_element_by_xpath(  ## 选择 物流方式
                        '//*[@id="purchase-create-identical"]/div[3]/form/div[1]/div[2]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[3]/div[1]/div[1]/ul/li[1]/span').click()

                    self.driver.find_element_by_xpath(  ## 选择 退回仓库
                        '//*[@id="purchase-create-identical"]/div[3]/form/div[1]/div[3]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[4]/div[1]/div[1]/ul/li[2]').click()

                    self.driver.find_element_by_css_selector(  ## 点击 保存并提交
                        '#purchase-create-identical > div.fx-button.fx-button-center > button.el-button.el-button--success.el-button--small').click()
                    break

            sleep(2)

            ## 获取采购换货单号
            self.driver.get(URLLIST['url_purchase_refundable_management'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#purchase-refundable-management > div.sales-management-table.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                purchase_return_order = self.driver.find_element_by_xpath(  ## 采购退换货单号字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                new_return_status = self.driver.find_element_by_xpath(  ## 退货状态字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[3]/div'.format(
                        sort=t + 1)).text
                logger.info('new_purchase_return_order %s,new_return_status %s', purchase_return_order, new_return_status)

                if new_return_status == '已提交':
                    break

            ## 获取 采购换货单对应的出库单号
            self.driver.get(URLLIST['url_outgoing_notice'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#outgoing-notice > div.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                outbound_order_number = self.driver.find_element_by_xpath(  ## 出库单号字段
                    '//*[@id="outgoing-notice"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/a'.format(
                        sort=t + 1)).text
                new_sales_order_number = self.driver.find_element_by_xpath(
                    '//*[@id="outgoing-notice"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(
                        sort=t + 1)).text
                logger.info('outbound_order_number %s,new_sales_order_number %s', outbound_order_number, new_sales_order_number)

                if new_sales_order_number == purchase_return_order:
                    self.wms_simulation_library_feedback(outbound_order_number)
                    break

            ## 获取 采购换货单对应的入库单号
            self.driver.get(URLLIST['url_warehousing_notice'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#warehousing-noticestorage-warehousing > div.fx-theme-table > div > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                inbound_order_number = self.driver.find_element_by_xpath(  ## 入库单号字段
                    '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/a'.format(
                        sort=t + 1)).text
                purchase_order_no = self.driver.find_element_by_xpath(  ## 采购字段
                    '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(
                        sort=t + 1)).text
                logger.info('inbound_order_number %s,purchase_order_no %s', inbound_order_number, purchase_order_no)

                if purchase_order_no == purchase_return_order:
                    self.wms_simulation_feedback_storage(inbound_order_number)
                    break

            ## 获取采购换货单的状态
            self.driver.get(URLLIST['url_purchase_refundable_management'])

            sleep(0.5)
            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                end_purchase_return_order = self.driver.find_element_by_xpath(  ## 采购退换货字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                new_return_status = self.driver.find_element_by_xpath(  ## 退货状态字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                        sort=t + 1)).text
                logger.info('end_purchase_return_order %s,new_return_status %s', end_purchase_return_order, new_return_status)

                if end_purchase_return_order == purchase_return_order:
                    self.assertEqual(new_return_status, '换货完成', '测试成功')
                    break
        except:
            self.img()
            raise

    @retry(wait=wait_random(min=10, max=20), stop=stop_after_attempt(3),before_sleep=before_sleep_log(logger, logging.DEBUG))
    def test_foreign_exchange(self):
        """
        测试异品换货，直到换货完成
        :return:
        """
        try:
            self.driver.get(URLLIST['url_inventory_warehouse'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#inventory-warehouse > div.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                new_quantity = self.driver.find_element_by_xpath( ## 数量字段
                    '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[8]/div'.format(
                        sort=t + 1)).text
                new_warehouse_name = self.driver.find_element_by_xpath( ## 仓库名称字段
                    '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                        sort=t + 1)).text
                logger.info('new_quantity %s,new_warehouse_name %s', new_quantity, new_warehouse_name)

                if new_quantity != 0: ## 如果库存数量不为0，则创建换货单
                    self.driver.find_element_by_xpath( ## 点击小框框
                        '//*[@id="inventory-warehouse"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/label/span/span'.format(
                            sort=t + 1)).click()

                    sleep(0.5)

                    self.driver.find_element_by_css_selector( ## 创建异品换货单
                        '#inventory-warehouse > div.fx-theme-button > div > button:nth-child(3) > span').click()

                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[12]/div/div/input'))
                    )
                    self.driver.find_element_by_xpath(  ## 输入退货数量
                        '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[12]/div/div/input').send_keys(
                        '2')

                    ## 添加货品
                    self.driver.find_element_by_css_selector(
                        '#purchase-create-identical > div:nth-child(2) > button').click()
                    self.driver.find_element_by_xpath(
                        '//*[@id="product-list"]/div[2]/div/div[3]/table/tbody/tr[3]/td[3]/div/button/span').click()
                    self.driver.find_element_by_css_selector(
                        '#purchase-create-identical > div.fx-mask > div > div > div.el-dialog__footer > span > button.el-button.el-button--primary.el-button--small').click()

                    self.driver.find_element_by_xpath(  ## 输入入库数量
                        '//*[@id="purchase-create-identical"]/div[3]/div/div[3]/table/tbody/tr/td[4]/div/div/input').send_keys(
                        '2')
                    purchase_price = self.driver.find_element_by_xpath(
                        '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[8]/div').text
                    cost_price = self.driver.find_element_by_xpath(
                        '//*[@id="purchase-create-identical"]/div[1]/div/div[3]/table/tbody/tr/td[9]/div').text
                    self.driver.find_element_by_xpath(  ## 输入采购单价
                        '//*[@id="purchase-create-identical"]/div[3]/div/div[3]/table/tbody/tr/td[5]/div/div/input').send_keys(
                        purchase_price)
                    self.driver.find_element_by_xpath(  ## 输入成本价
                        '//*[@id="purchase-create-identical"]/div[3]/div/div[3]/table/tbody/tr/td[6]/div/div/input').send_keys(
                        cost_price)

                    self.driver.find_element_by_xpath(  ## 输入收货人
                        '//*[@id="purchase-create-identical"]/div[4]/form/div[1]/div[2]/div/div[1]/input').send_keys(
                        '吴平')

                    self.driver.find_element_by_css_selector(  ## 选择收货人地址
                        '#city-picker-template > span').click()
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                    "#city-picker-template > div"))
                    )
                    self.driver.find_element_by_css_selector(  ## 选择省份
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.province > dl:nth-child(1) > dd > a:nth-child(6)').click()
                    self.driver.find_element_by_css_selector(  ## 选择城市
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.city > dl > dd > a:nth-child(11)').click()
                    self.driver.find_element_by_css_selector(  ## 选择县区
                        '#city-picker-template > div > div > div.region-select-content > div.region-select.district > dl > dd > a:nth-child(2)').click()

                    self.driver.find_element_by_xpath(  ## 输入详细地址
                        '//*[@id="purchase-create-identical"]/div[4]/form/div[2]/div[1]/div/div[1]/input').send_keys(
                        '惠州市惠阳区经济开发区三和大道嘉民产业园207门口')

                    self.driver.find_element_by_xpath(  ## 选择是否开票:否
                        '//*[@id="purchase-create-identical"]/div[5]/form/div[1]/div[1]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[2]/div[1]/div[1]/ul/li').click()

                    self.driver.find_element_by_xpath(  ## 选择 物流方式
                        '//*[@id="purchase-create-identical"]/div[5]/form/div[1]/div[2]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[3]/div[1]/div[1]/ul/li[2]/span').click()

                    self.driver.find_element_by_xpath(  ## 选择 退回仓库
                        '//*[@id="purchase-create-identical"]/div[5]/form/div[1]/div[3]/div/div/div[1]/input').click()
                    self.driver.find_element_by_xpath(
                        '/html/body/div[4]/div[1]/div[1]/ul/li[2]').click()

                    self.driver.find_element_by_css_selector(  ## 点击 保存并提交
                        '#purchase-create-identical > div.fx-button.fx-button-center > button.el-button.el-button--success.el-button--small > span').click()
                    break

            sleep(2)

            ## 获取采购换货单号
            self.driver.get(URLLIST['url_purchase_refundable_management'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#purchase-refundable-management > div.sales-management-table.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                new_purchase_return_order = self.driver.find_element_by_xpath(  ## 采购退换货单号字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                new_return_status = self.driver.find_element_by_xpath(  ## 退货状态字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                        sort=t + 1)).text
                logger.info('new_purchase_return_order %s,new_return_status %s', new_purchase_return_order, new_return_status)

                if new_return_status == '已提交':
                    break

            ## 获取 采购换货单对应的出库单号
            self.driver.get(URLLIST['url_outgoing_notice'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#outgoing-notice > div.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                outbound_order_number = self.driver.find_element_by_xpath(  ## 出库单号字段
                    '//*[@id="outgoing-notice"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/a'.format(
                        sort=t + 1)).text
                new_sales_order_number = self.driver.find_element_by_xpath(
                    '//*[@id="outgoing-notice"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(
                        sort=t + 1)).text
                logger.info('outbound_order_number %s,new_sales_order_number %s', outbound_order_number, new_sales_order_number)

                if new_sales_order_number == new_purchase_return_order:
                    self.wms_simulation_library_feedback(outbound_order_number)
                    break

            ## 获取 采购换货单对应的入库单号
            self.driver.get(URLLIST['url_warehousing_notice'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#warehousing-noticestorage-warehousing > div.fx-theme-table > div > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                inbound_order_number = self.driver.find_element_by_xpath(  ## 入库单号字段
                    '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[{sort}]/td[1]/div/a'.format(
                        sort=t + 1)).text
                purchase_order_no = self.driver.find_element_by_xpath(  ## 采购字段
                    '//*[@id="warehousing-noticestorage-warehousing"]/div[3]/div/div/div[3]/table/tbody/tr[{sort}]/td[2]/div'.format(
                        sort=t + 1)).text
                logger.info('inbound_order_number %s,purchase_order_no %s', inbound_order_number, purchase_order_no)

                if purchase_order_no == new_purchase_return_order:
                    self.wms_simulation_feedback_storage(inbound_order_number)
                    break

            ## 获取采购换货单的状态
            self.driver.get(URLLIST['url_purchase_refundable_management'])

            table_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#purchase-refundable-management > div.sales-management-table.fx-theme-table > div > div.el-table__body-wrapper.is-scrolling-none > table > tbody"))
            )
            table_row_list = table_element.find_elements_by_tag_name('tr')
            logger.info('Successful table_row_list')
            for t, tr in enumerate(table_row_list):  ## 遍历表格内容
                end_purchase_return_order = self.driver.find_element_by_xpath(  ## 采购退换货字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[2]/div/a'.format(
                        sort=t + 1)).text
                new_return_status = self.driver.find_element_by_xpath(  ## 退货状态字段
                    '//*[@id="purchase-refundable-management"]/div[3]/div/div[3]/table/tbody/tr[{sort}]/td[4]/div'.format(
                        sort=t + 1)).text
                logger.info('end_purchase_return_order %s,new_return_status %s', end_purchase_return_order, new_return_status)

                if end_purchase_return_order == new_purchase_return_order:
                    self.assertEqual(new_return_status, '换货完成', '测试成功')
                    break
        except:
            self.img()
            raise

if __name__ == '__main__':
    unittest.main()
