import csv
import eel
import desktop
import pos_system as ps



app_name="html"
end_point="index.html"
size=(700,600)

# マスタ登録
item_master = []

# 売り上げデータ
sales = ps.Sales('sales.csv')

# オーダー登録
order = ps.Order(item_master, sales)

@ eel.expose
def read_master(csv_path):
    ps.register_item_master_from_csv(csv_path, item_master)

@ eel.expose
def add_item_order(item_code, item_quantity):
    order.add_item_order(item_code, item_quantity)
    eel.view_order_js(order.get_item_order_text(-1))
    
@ eel.expose
def get_sum():
    return order.get_sum()

@ eel.expose
def checkout(payment):
    change = order.checkout(int(payment))
    if change >= 0:
        order.write_receipt()
        order.add_order_to_sales()
    return change

@ eel.expose
def clear_order():
    order.clear_order()
    
desktop.start(app_name,end_point,size)
#desktop.start(size=size,appName=app_name,endPoint=end_point)