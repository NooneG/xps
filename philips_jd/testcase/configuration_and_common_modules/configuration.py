#-*- coding:utf-8 -*-
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

# StreamHandler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# FileHandler
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

URLLIST = {
    ## 采购订单管理
    'url_purchase_order_management':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/PurchaseOrderManagement',
    ## 采购换货管理
    'url_purchase_refundable_management': 'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/PurchaseRefundableManagement',
    ## 仓库库存查询
    'url_inventory_warehouse':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/InventoryWarehouse',
    ## 入库通知单管理
    'url_warehousing_notice':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/WarehousingNotice',
    ## 出库通知单管理
    'url_outgoing_notice':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/OutgoingNotice',
    ## 订单管理
    'url_order_management':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/OrderManagement',
    ## 销售退换货管理
    'url_sales_returns_management':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/SalesReturnsManagement',
    ## 售后退货管理
    'url_after_sales_management':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/AfterSalesManagement',
    ## EDI中心，采购订单导入查询
    'url_EDIPurchase':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/EDIPurchase',
    ## EDI中心，发货确认导入查询
    'url_EDIDelivery':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/EDIDelivery',
    ## EDI中心，退货单导入管理
    'url_EDIReturns':'http://47.104.154.165:20020/philips/jd/fenxiao/main/#/EDIReturns',

    ## 模拟WMS
    'url_simulate_WMS':'http://47.104.154.165:58008/simulate/main/wms/index.html#/SimulateWMS'
}






