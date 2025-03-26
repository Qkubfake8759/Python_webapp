from flask import Flask , render_template, request,redirect, url_for 
from connecttion import connection_database, execute_data, execute_data_insert
import requests



app = Flask(__name__, template_folder="template")
LINE_NOTIFY_TOKEN = "7lVpHVzPrquKZ3M4aucCt7SBuXj5tMfw8oWuQSqQTWx"



@app.route("/home", methods=['GET', 'POST'])
def home():



    order_text = ""
    stock_text = ""
    stock_textgrp = ""
    customer_text = ""
    customergrp_text = ""
    select = ""

    button_serch = request.form.get("button_serch")
    button_add = request.form.get("button_add")
    button_edit = request.form.get("button_edit")
    button_delete = request.form.get("button_delete")
    button_select_edit = request.form.get("button_select_edit")
    search_tb_button = request.form.get("search_tb_button")
    search_tb_text = request.form.get("search_tb_text")


    
    result = connection_database()

    if result > 0:
        
        search_tb_text = request.form.get("search_tb_text")
        query = "SELECT * FROM tbSale"
        order_text = execute_data(query)
        
        select_stock = request.form.get("stock")
        select_value = request.form.get("customer")
        custcode = select_value

        query = "SELECT * FROM tbCustomer"
        result_customer = execute_data(query)
        customer_text = result_customer

        query = "SELECT * FROM tbStock"
        result_stock = execute_data(query)
        stock_text = result_stock

        query = "SELECT * FROM tbStockGrp"
        result_stockgrp = execute_data(query)
        stock_textgrp = result_stockgrp

        if select_value == "":
            select_value = None

        if 'button_serch' in request.form:
            print("ค้นหา", select_value)



            if select_value is not None:

                for row in customer_text:
                    if select_value == row[0]:
                        customergrp_text = row[1]

                query = "SELECT CustGrpName FROM tbCustomerGrp where CustGrpCode = '" + customergrp_text + "'"
                result_customergrp = execute_data(query) 
                
                for result_text in result_customergrp:
                    customergrp_text=result_text[0]
                    print("customergrp_text", customergrp_text)
            else:
                print("Select value is None")

        elif 'search_tb_button' in request.form:
            search_tb_button = request.form.get("search_tb_text")
            print("Search Text",search_tb_text)

            query = "SELECT * FROM tbSale WHERE SOCode = '" + search_tb_text + "'"
            order_text = execute_data(query)
            print(order_text)
            if order_text is None:
                print("Not Found")
                return redirect(url_for("home"))
            else:
                print("Found Data")
                return render_template("home/home.html",
                            search_tb_text=search_tb_text,
                            button_select_edit=button_select_edit,
                            select_value=select_value,
                            select_stock=select_stock,
                            customer_text=customer_text,
                            stock_text=stock_text,
                            stock_textgrp=stock_textgrp,
                            customergrp_text=customergrp_text,
                            order_text=order_text
                            )
    

        
        elif 'button_add' in request.form:
            select_value = request.form.get('customer')  # รหัสลูกค้า
            select_stock = request.form.get('stock')  # รหัสสินค้า

            if not select_value or not select_stock:
                print("ข้อมูลไม่ครบถ้วน")
                return redirect(url_for("home"))

            # ดึงข้อมูลลูกค้า
            query = f"SELECT CustName, CustTel, CustGrpCode FROM tbCustomer WHERE CustCode = '{select_value}'"
            customer_data = execute_data(query)

            if customer_data:
                cust_name, phone, cust_grp_code = customer_data[0]

                # ดึงประเภทลูกค้า
                query = f"SELECT CustGrpName FROM tbCustomerGrp WHERE CustGrpCode = '{cust_grp_code}'"
                customer_grp_data = execute_data(query)
                cust_type = customer_grp_data[0][0] if customer_grp_data else "ไม่ระบุ"

                # ดึงชื่อสินค้า
                query = f"SELECT StockName FROM tbStock WHERE StockCode = '{select_stock}'"
                stock_data = execute_data(query)
                product_name = stock_data[0][0] if stock_data else "ไม่ระบุ"

                # บันทึกลงฐานข้อมูล
                query = f"INSERT INTO tbSale (CustCode, StockCode, StockGrpCode) VALUES ('{select_value}', '{select_stock}', '{cust_grp_code}')"
                execute_data_insert(query)

                # ส่งการแจ้งเตือนไปที่ LINE
                send_line_notify(cust_name, phone, cust_type, product_name)

                return redirect(url_for("home"))

    
        elif 'button_select_edit' in request.form:
            button_select_edit = request.form.get("button_select_edit")  # รับค่าจากฟอร์ม
            print("แก้ไข", button_select_edit)

            if order_text:  # เช็คว่ามีข้อมูลใน order_text ไหม
                for row in order_text:
                    if str(row[0]) == str(button_select_edit):  # แปลงเป็น string ก่อนเช็ค
                        print("พบข้อมูลที่ต้องการแก้ไข:", row[0])

                        select_value = row[1]
                        select_stock = row[2]

                        for row in customer_text:
                            if select_value == row[0]:
                                customergrp_text = row[1]

                        query = "SELECT CustGrpName FROM tbCustomerGrp where CustGrpCode = '" + customergrp_text + "'"
                        result_customergrp = execute_data(query)
                        
                        for result_text in result_customergrp:
                            customergrp_text = result_text[0]

                        print("Select stock:", select_stock)
                        print("Select value:", select_value)

                        select = button_select_edit
                        
                        print("Select", select)
            else:
                print("ไม่มีข้อมูลให้แก้ไข")

        
        elif 'button_edit' in request.form:
            button_edit = request.form.get("button_edit")
            print("แก้ไข", button_edit)

            select_value = request.form.get('customer')
            select_stock = request.form.get('stock')

            print("Select value Edit:", custcode)
            print("Select stock: Edit", select_stock)

            custcode = select_value

            if select_value and select_stock is not None:
                for row in stock_text:
                    
                    if select_stock == row[0]:
                        result = row[1]
                        stockgrp_code = result
                        if custcode  is None:
                            print("Select value is None")
                            return redirect(url_for("home"))
                        elif select_stock is None:
                            print("Select stock is None")
                            return redirect(url_for("home"))
                        elif stockgrp_code is None:
                            print("StockGrp is none")
                            return redirect(url_for("home"))
                        elif button_edit is None:
                            print("NO point to update")
                            return redirect(url_for("home"))
                        else:
                            print("Update: ", button_edit)
                            query = f"UPDATE tbSale SET CustCode = '{custcode}', StockCode = '{select_stock}', StockGrpCode = '{stockgrp_code}' WHERE SOCode = '{button_edit}'"
                            print("update: ",execute_data_insert(query))
                            
                            

                            select_value = None
                            select_stock = None
                            custcode = None
                            button_select_edit = None

                            return redirect(url_for("home"))
            else:
                        print("data to update is wrong")
                        return redirect(url_for("home"))
        
        elif 'button_delete' in request.form:
            button_delete = request.form.get("button_delete")
            print("ลบ", button_delete)

            try:
                print("Delete:", button_delete)
                query = "DELETE tbSale WHERE SOCode =" + button_delete
                print("Delete Suc", execute_data_insert(query))
                
                return redirect(url_for("home"))
            except Exception as e:
                print(e)
                return redirect(url_for("home"))
            
            
            
    else:
        print("Connect database failed")
        return redirect(url_for("home"))
    return render_template("home/home.html",
                            search_tb_text=search_tb_text,
                            button_select_edit=button_select_edit,
                            select_value=select_value,
                            select_stock=select_stock,
                            customer_text=customer_text,
                            stock_text=stock_text,
                            stock_textgrp=stock_textgrp,
                            customergrp_text=customergrp_text,
                            order_text=order_text
                            )

def send_line_notify(cust_name, phone, cust_type, product,):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer 7lVpHVzPrquKZ3M4aucCt7SBuXj5tMfw8oWuQSqQTWx",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    message = (
        "CDTI_Notify: 📢\nร้าน จักรยานสะท้านโลก\nข้อมูลการสั่งสินค้าใหม่\n"
        f"👤 ลูกค้า: {cust_name}\n"
        f"📞 เบอร์โทร: {phone}\n"
        f"🏷️ ประเภทลูกค้า: {cust_type}\n"
        f"📦 สินค้า: {product}"
        
    )
    

    data = {"message": message}
    requests.post(url, headers=headers, data=data)



   
  


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = int(request.form.get('product_id'))
    global products
    products = [p for p in products if p['id'] !=product_id]
    return redirect(url_for('home'))


@app.route("/customer")
def customer():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbCustomer"
        result_customer = execute_data(query)
        if result_customer:
            customer_text = result_customer
            print(customer_text)
        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("customer/customer.html",customer_text=customer_text)

@app.route("/customergrp")
def customergrp():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbCustomerGrp"
        result_customergrp = execute_data(query)

        if result_customergrp:
            customergrp_text = result_customergrp
            print("customergrp_text")

        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("customergrp/customergrp.html",customergrp_text=customergrp_text)

@app.route("/stock")
def stock():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbStock"
        result_stock = execute_data(query)
        if result_stock:
            stock_text = result_stock
        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("stock/stock.html",stock_text=stock_text)

@app.route("/stockgrp")
def stockgrp():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbStockGrp"
        result_stockgrp = execute_data(query)
        if result_stockgrp:
            stock_textgrp = result_stockgrp
        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("stockgrp/stockgrp.html",stock_textgrp=stock_textgrp)

@app.route("/saletype")
def saletype():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbSaleType"
        result_saletype = execute_data(query)
        if result_saletype:
            saletype_text = result_saletype
        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("saletype/saletype.html",saletype_text=saletype_text)

@app.route("/location")
def location():
    result = connection_database()

    if result > 0:
        query = "SELECT * FROM tbLocation"
        result_location = execute_data(query)
        if result_location:
            location_text = result_location
        else:
            print("fa")
        conn_text = "สำเร็จ"
    else:
        conn_text = "ไม่สำเร็จ"
    return render_template("location/location.html",location_text=location_text)

if __name__ == "__main__":
    app.run(debug=True)