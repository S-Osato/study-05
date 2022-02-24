### 商品クラス
from numpy import quantile
from pyparsing import null_debug_action
import os
import csv
import pandas as pd
import datetime
import eel

class Item:
    def __init__(self,item_code,item_name,price):
        self.item_code=item_code
        self.item_name=item_name
        self.price=price
    
    def get_price(self):
        return self.price
    
    def get_item_code(self):
        return self.item_code
    
    def get_item_name(self):
        return self.item_name

class Receipt:
    def __init__(self):
        self.text = ''
    
    def add_text(self, text):
        self.text += text + "\n"

    def print_receipt(self):
        print(self.text)
        
    def write_receipt(self):
        # 年月日毎にレシートフォルダを作成する
        now = datetime.datetime.now()
        now_str = now.strftime("%Y%m%d_%H%M%S")
        dir = f"receipts/{now.year}/{now.month}/{now.day}/"
        os.makedirs(dir, exist_ok=True)
        path = os.path.join(dir, f"receipt_{now_str}.txt")
        with open(path, mode='w', encoding="utf-8") as text_file:
            text_file.write(self.text)
        
        #テキストリセット
        self.text = ""
        
### オーダークラス
class Order:
    def __init__(self,item_master, sales):
        self.item_order_list=[]
        self.item_master=item_master
        self.sum = 0
        self.recipt = Receipt()
        self.sales = sales
    
    def add_item_order(self,item_code, item_quantity):
        searched_item = self.search_item(item_code)
        if not searched_item:
            eel.show_alert_js(f"商品コード:{item_code}はありません。")
        else:
            self.item_order_list.append({'code': item_code, 'quantity': item_quantity})
            price = int(searched_item.get_price())
            quantity = int(item_quantity)
            
            self.sum +=  price * quantity
    
    def get_sum(self):
        return self.sum
    
    def get_item_order_text(self, index):
        if len(self.item_order_list) > 0:
            item = self.item_order_list[index]
            searched_item = self.search_item(item['code'])
            price = int(searched_item.get_price())
            quantity = int(item['quantity'])
                    
            item_name_text = "商品名:{}".format(searched_item.get_item_name())
            item_price_text = "価格:{}".format(price)
            item_quantity_text = "個数:{}".format(quantity)
            return f"{item_name_text} {item_price_text} {item_quantity_text}\n"
        else:
            return ""
        
    def search_item(self, item_code):
        for item in self.item_master:
            if item.get_item_code() == item_code:
                return item
        return None
            
    def create_recipt(self):
        for item in self.item_order_list:
            searched_item = self.search_item(item['code'])
            if not searched_item:
                eel.show_alert_js(f"商品コード:{item['code']}はありません。")
            else:
                price = int(searched_item.get_price())
                quantity = int(item['quantity'])
                
                item_name_text = "商品名:{}".format(searched_item.get_item_name())
                item_price_text = "価格:{}".format(price)
                item_quantity_text = "個数:{}".format(quantity)
                
                self.recipt.add_text(f"{item_name_text} {item_price_text} {item_quantity_text}")
                
                self.sum +=  price * quantity
        
        sum_text = "合計金額:{}".format(self.sum)
        self.recipt.add_text(f"{sum_text}")

    def print_receipt(self):
        self.recipt.print_receipt()
        
    def checkout(self, payment):
        change =  payment - self.sum
        if change >= 0:
            print(f"お釣り:{change}")
            self.create_recipt()
            self.recipt.add_text(f"お釣り:{change}")
            return change
        else:
            eel.show_alert_js("お預かり金額がたりません。")
            return None
        
    def write_receipt(self):
        self.recipt.write_receipt()
        
    def add_order_to_sales(self):
        for item in self.item_order_list:
            searched_item = self.search_item(item['code'])
            price = int(searched_item.get_price())
            self.sales.add_sales(item["code"], int(item["quantity"]), price)
        
    def clear_order(self):
        self.item_order_list=[]
        self.sum = 0
        self.recipt = Receipt()
        
### 売上クラス
class Sales:
    def __init__(self, data_path):
        self.data_path = data_path
        self.sales_data = pd.DataFrame()
        self.read_sales_data()

    def read_sales_data(self):
        if os.path.exists(self.data_path):
            self.sales_data = pd.read_csv(self.data_path,header=0,dtype={'商品コード': str,'売上個数': int, '売上金額': int})
        else:
            self.sales_data = pd.DataFrame(columns=["商品コード", "売上個数", "売上金額"])
    
    def add_sales(self, item_code, item_quatity, item_price):
        tmp_df = self.sales_data[self.sales_data['商品コード'] == item_code]
        if not tmp_df.empty:
            self.sales_data.loc[self.sales_data['商品コード'] == item_code, '売上個数'] = tmp_df['売上個数'] + item_quatity
            self.sales_data.loc[self.sales_data['商品コード'] == item_code, '売上金額'] = tmp_df['売上金額'] + item_price*item_quatity
        else:
            tmp_df = [{"商品コード":item_code, "売上個数":item_quatity, "売上金額":item_price*item_quatity}]
            self.sales_data = self.sales_data.append(tmp_df,ignore_index=True)
        
        self.sales_data.to_csv(self.data_path,index=False)
    
def register_item_master_from_csv(csv_path, item_master):
    if os.path.exists(csv_path):
        print(f"{csv_path}をアイテムマスタに登録します。")
        with open(csv_path) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                item_master.append(Item(row[0], row[1], row[2]))
    else:
        eel.show_alert_js(f"{csv_path}がありません。")
        

