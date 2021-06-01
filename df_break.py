import csv
import requests
import json
import tkinter as tk
from bpsot import Bpost
from box import  Box
import tkinter.font as tkFont
import os
import time
import math
import configparser
#import pandas as pd

config = configparser.ConfigParser()
config.read('invoice.ini')
url = "http://192.117.139.143:57772/rest/api/Shop/DeliveryFileToJsonPayable/"
fields=['Supplier','Invoice#','Invoice Date','Total Invoice','Tracking#','Operation Date', 'Service Type','Entity Type',
        'Entity#', 'Charge Type','Amount','Charge description','Charge Type','Amount'
        ,'Charge description','Charge Type', 'Amount','Charge description','Total Amount','Gross Weight','Weight UOM', 'Packages Quantity',
        'Supplier Reference(Numbern3)','To Country', 'From Country','To Zip', 'From Zip', 'Currency', 'Carrier','Chargable Weight']

window_keys = ['title', 'supplier', 'supplier_code', 'invoice_number', 'invoice_number',
               'invoice_date','currency', 'invoice_amount']
df_list = []
file_name = 'inv.csv'
r = tk.Tk()

global invoice_data_map
global invoice_data_map_test
global error
global delivery_file
frame = tk.Frame(r)
title_font_style = tkFont.Font(family="Lucida Grande", size=16)
regular_font_style = tkFont.Font(family="Lucida Grande", size=12)
error_font_style = tkFont.Font(family="Lucida Grande", size=8)
global continue_flag
global first_flag
first_flag = True
global charge_first_flag
charge_first_flag =True

def initialize():
    global invoice_data_map
    global error
    global delivery_file
    invoice_data_map = {'supplier': tk.StringVar(), 'supplier_code': tk.StringVar(), 'invoice_number': tk.StringVar(),
                        'invoice_date': tk.StringVar(), 'currency': tk.StringVar(),
                        'invoice_amount': tk.StringVar(), 'operational_number': tk.StringVar(), 'chargeable_weight':
                            tk.StringVar(), 'charge_type': tk.StringVar(), 'number_of_bposts':tk.StringVar(), 'tracking_number':tk.StringVar(),
                        'vat':tk.StringVar(),'air_trans_nis':tk.StringVar(), 'air_trans_usd':tk.StringVar(), 'invoice_amount_nis':tk.StringVar(),
                        "dollar_exchange_rate":tk.StringVar(), 'vat_usd':tk.StringVar()}
    error = tk.StringVar()
    delivery_file = tk.StringVar()    

def abort(message):
    print(message)
    clear_frame()
    tk.Label(frame, text=message).grid(row=0)

def create_csv_file(file_name):
    with open(file_name, 'w', newline='') as of:
        writer = csv.writer(of)
        writer.writerow(fields)

def clear_frame():
    for widget in frame.winfo_children():
        widget.destroy()

def calc_invoice_amount():
    vat,air_trans_nis,air_trans_usd,amount_nis = invoice_data_map['vat'],invoice_data_map['air_trans_nis'],invoice_data_map['air_trans_usd'],invoice_data_map['invoice_amount_nis']
    dollar_exchange_rate = round(float(air_trans_nis) / float(air_trans_usd),2)
    vat_usd = round(float(vat) / float(dollar_exchange_rate),2)
    amount_usd = round(float(amount_nis) / float(dollar_exchange_rate),2)
    total_amount_usd = round(amount_usd - vat_usd,2)
    invoice_data_map['invoice_amount'] = str(total_amount_usd)
    invoice_data_map['vat_usd'] = str(vat_usd)
    invoice_data_map['dollar_exchange_rate'] = str(dollar_exchange_rate)


def handel_invocie_data():
    
    if invoice_data_validation():
        clear_frame()
        if invoice_data_map['supplier_code'] =='UPS' or invoice_data_map['supplier_code'] =='DSV':
            calc_invoice_amount()
        df = get_delivery_file()
        if len(df['DeliveryFiles']) == 0:
            create_no_delivery_files_window()
        else:
            for delivery_file in df['DeliveryFiles']:
                df_list.append(delivery_file['DeliveryID'])
            create_delivery_file_win(df['DeliveryFiles'])

def create_no_delivery_files_window():
    clear_frame()
    tk.Label(frame, text='no delivery file found for tracking number: ' + invoice_data_map["tracking_number"],
             font=regular_font_style).grid(row=0, columnspan=10)


def get_delivery_file():
    url ='http://192.117.139.143:57772/rest/api/Shop/GetDeliveryFilesByTRK/' + invoice_data_map['tracking_number']
    response = requests.request("POST", url, headers={}, data={})
    response_json = json.loads(response.text)
    return response_json


def invoice_data_validation():
    error.set('')
    if invoice_data_map['supplier'].get() == '':
        error.set("please enter supplier")
        return False
    if invoice_data_map['supplier_code'].get() == '':
        error.set("please enter supplier code")
        return False
    if invoice_data_map['invoice_number'].get() == '':
        error.set("please enter invoice number")
        return False
    if invoice_data_map['invoice_date'].get() == '':
        error.set("please enter invoice date")
        return False
    if invoice_data_map['currency'].get() == '' and invoice_data_map['supplier_code'].get() == 'FBG':
        error.set("please enter currency")
        return False
    if invoice_data_map['operational_number'].get() == '':
        error.set("please enter Supplier Reference")
        return False
    if invoice_data_map['invoice_amount'].get() == '' and  invoice_data_map['supplier_code'].get() == 'FBG':
        error.set("please enter invoice_amount")
        return False
    if invoice_data_map['chargeable_weight'].get() == '' and invoice_data_map['supplier_code'].get() != 'FBG':
        error.set("please enter chargeable_weight")
        return False
    if invoice_data_map['number_of_bposts'].get() == '' and invoice_data_map['supplier_code'].get() == 'FBG':
        error.set("please enter number of bposts for FBG")
        return False
    if (invoice_data_map['supplier_code'].get() == 'UPS' or invoice_data_map['supplier_code'].get() == 'DSV') \
            and invoice_data_map['vat'].get() == '':
        error.set("please enter invoice vat NIS")
        return False
    if (invoice_data_map['supplier_code'].get() == 'UPS' or invoice_data_map['supplier_code'].get() == 'DSV') \
            and invoice_data_map['invoice_amount_nis'].get() == '':
        error.set("please enter invoice amount NIS")
        return False
    if (invoice_data_map['supplier_code'].get() == 'UPS' or invoice_data_map['supplier_code'].get() == 'DSV') \
            and invoice_data_map['air_trans_nis'].get() == '':
        error.set("please enter Air Transport NIS")
        return False
    if (invoice_data_map['supplier_code'].get() == 'UPS' or invoice_data_map['supplier_code'].get() == 'DSV') \
            and invoice_data_map['air_trans_usd'].get() == '':
        error.set("please enter Air Transport USD")
        return False
    for key in invoice_data_map.keys():
        invoice_data_map[key] = invoice_data_map[key].get()
    return True

def get_data_from_service(headers,payload,url, df):
    url = url + str(df)
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = json.loads(response.text)
    return response_json


def get_charge_description():
    if invoice_data_map['charge_type'] == 'FLR':
        return 'First Leg (Replenishment)'
    if invoice_data_map['charge_type'] == 'CUC':
        return 'Customs Clearance'
    return ''

def write_data_to_csv(box_list, file_name):
    with open(file_name, 'a', newline='') as of:
        writer = csv.writer(of)
        for box in box_list:
            for bpost in box.bpost_list:
                writer.writerow([invoice_data_map['supplier_code'],invoice_data_map['invoice_number'],invoice_data_map['invoice_date'],
                                invoice_data_map['invoice_amount'], bpost.awb, bpost.operation_date, bpost.service_type,'bpost',
                                bpost.number,  get_charge_type(bpost), bpost.amount, get_charge_description(), '','','','','','',
                                 bpost.amount, bpost.weight,
                                 bpost.weight_UOM, '1', invoice_data_map['operational_number'],
                                bpost.to_country, bpost.from_country, bpost.to_country_zip, bpost.from_country_zip,
                                invoice_data_map['currency'], bpost.carrier, bpost.chargeable_weight])

def get_charge_type(bpost):
    global charge_first_flag
    max = 0
    flag_exist = False
    charge_type =invoice_data_map['charge_type']
    for charge in bpost.charges:
        if charge_type in charge:
            flag_exist = True
            split_array = charge_type.split(charge_type)
            try:
                if max < int(split_array[1]):
                    max = int(split_array[1])
            except:
                pass
    if flag_exist:
        if charge_first_flag:
            create_new_charge_type(charge_type + str(max + 1))
            charge_first_flag =False
        return  charge_type + str(max + 1)
    else:
        return charge_type

def create_new_charge_type(charge_type):
    u = 'http://192.117.139.143:57772/rest/api/Shop/CreateNewPaybleChargeType/' + charge_type + '/' + get_charge_description()
    response = requests.request("POST", u, headers={}, data={})
    print(response.text)




def delete_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        abort("text file" + file_name +" The file does not exist")

def convert_csv_to_text(file_name):
    try:
        with open(file_name, 'r') as inp, open(file_name.split('.')[0] + '.text', 'w') as out:
            for line in inp:
                line = line.replace(',', '\t')
                out.write(line)
    except Exception as e:
        abort(e)

def move_file_to_service_dir(file_name):
    try:
        batch_file = 'copy_file.bat'
        comm = batch_file + ' ' + file_name
        os.system(comm)
    except Exception as e:
        abort(e)


def move_file_to_ftp(file_name):
    url = "http://192.117.139.227/Magicxpi4.7/MgWebRequester.dll"

    querystring = {"appname": "IFSInvocieBreaker", "prgname": "HTTP", "arguments": "-AHTTP_4%23Trigger1",
                   "invoice_number": invoice_data_map['invoice_number'], "supplier": invoice_data_map['supplier_code']}
    payload = ""
    headers = {}
    with open(file_name, 'rb') as f:
        try:
            response = requests.request("POST", url, data=f, headers=headers, params=querystring)
            if response.text == '0' or response.text == '':
              abort('Failed to move file to ftp')
        except Exception as e:
            abort(e)

def boxes_chargeable_sum(box_list):
    total = 0
    for box in box_list:
        total = total + box.chargeable_weight
    return total

def process_df_data(data_json, box_list):
    for box in data_json["Boxes"]:
        b = Box(box['boxNumber'], box['DIM'])
        b.calc_chargeable_weight(6000)
        box_list.append(b)
        try:
            for delivery in box["deliveries"]:
                b.add_bpost(Bpost(delivery["DeliveryId"], round(float(delivery["Weight"]),2), data_json["AWB"],
                                delivery["OperationDate"].split()[0],  data_json["FromCountry"],
                                data_json["ToCountry"],  data_json["FromZip"],data_json["ToZip"],
                                data_json["Carrier"],data_json["ServiceType"],data_json["WeightUOM"],delivery["chargesList"])
                                )
        except Exception as e:
            print(e)

    kg_charge = round(float(invoice_data_map['invoice_amount'])/ boxes_chargeable_sum(box_list),2)
    number_of_bposts = calculate_number_of_bposts(box_list)
    for box in box_list:
        if invoice_data_map['supplier_code'] != 'FBG':
            calc_chargeable_weight(box)
            # fix_chargeable_box(b)
            calc_amount(kg_charge, box)


def fix_chargeable_box(box):
    total_ch = 0
    for bpost in box.bpost_list:
        total_ch = total_ch + bpost.chargeable_weight
    if total_ch != round(box.chargeable_weight, 2):
        dif_ch = round(round(box.chargeable_weight, 2) - round(total_ch,2), 2)
        bpost.set_chargeable_weight(round(bpost.chargeable_weight - dif_ch, 2))


def get_chargeable_weight_amount_dif(box_list):
    total_ch = 0
    total_am = 0
    dif_am = 0
    dif_ch = 0
    for box in box_list:
        for bpost in box.bpost_list:
            total_ch = total_ch + bpost.chargeable_weight
            total_am = total_am + bpost.amount
    if total_ch != round(float(invoice_data_map['chargeable_weight']), 2):
        dif_ch = round(round(float(invoice_data_map['chargeable_weight']), 2) - total_ch, 2)
    if total_am != round(float(invoice_data_map['invoice_amount']), 2):
        dif_am = round(round(float(invoice_data_map['invoice_amount']), 2) - total_am, 2)
    return dif_am, dif_ch


def fix_amount_fbg(box_list):
    total_am = 0
    dif_am = 0
    for box in box_list:
        for bpost in box.bpost_list:
            total_am = total_am + bpost.amount
    if total_am != round(float(invoice_data_map['invoice_amount']), 2):
        dif_am = round(round(float(invoice_data_map['invoice_amount']), 2) - total_am, 2)
    flag_am = False
    while dif_am > 0:
        for box in box_list:
            for bpost in box.bpost_list:
                if not flag_am:
                    if dif_am > 0:
                        bpost.set_amount(round(bpost.amount + 0.01, 2))
                        dif_am = round(dif_am - 0.01,2)
                    else:
                        if dif_am ==0:
                            flag_am = True
                            break;
                        if dif_am + 0.01 <= 0:
                            bpost.set_amount(round(bpost.amount + 0.01 , 2))
                            dif_am = dif_am + 0.01
                        else:
                            bpost.set_amount(round(bpost.amount + dif_am, 2))
                            flag_am = True
                            break;
            if flag_am:
                break

def fix_chargeable_weight_amount(box_list):
    total_ch = 0
    total_am = 0
    dif_am = 0
    dif_ch = 0
    for box in box_list:
        for bpost in box.bpost_list:
            total_ch = total_ch + bpost.chargeable_weight
            total_am = total_am + bpost.amount
    if total_ch != round(float(invoice_data_map['chargeable_weight']), 2):
        dif_ch = round(round(float(invoice_data_map['chargeable_weight']), 2) - total_ch, 2)
    if total_am != round(float(invoice_data_map['invoice_amount']), 2):
        dif_am = round(round(float(invoice_data_map['invoice_amount']), 2) - total_am, 2)
    #dif_ch = dif_ch / float(len(box_list))
    #dif_am = dif_am / float(len(box_list))
    flag_ch = False
    flag_am = False
    for box in box_list:

        for bpost in box.bpost_list:
            if not flag_am:
                if dif_am > 0:
                    bpost.set_amount(round(bpost.amount + dif_am, 2))
                    flag_am = True
                    break
                else:
                        if dif_am + bpost.amount > 0:
                            bpost.set_amount(round(bpost.amount + dif_am, 2))
                            flag_am = True
                            break
        if flag_am:
            break
        '''
              for bpost in box.bpost_list:
            if not flag_ch:
                if dif_ch > 0:
                    bpost.set_chargeable_weight(round(bpost.chargeable_weight + dif_ch, 2))
                    flag_ch = True
                    break
                else:
                    if dif_ch + bpost.chargeable_weight > 0:
                        bpost.set_chargeable_weight(round(bpost.chargeable_weight + dif_ch, 2))
                        flag_ch = True
                        break
    
        
        if dif_ch >0:
            bpost.set_chargeable_weight(round(bpost.chargeable_weight + dif_ch, 2))
        else:
            while dif_ch < 0:
                if dif_ch + bpost.chargeable_weight <= 0:
                    dif = bpost.chargeable_weight - 0.1
                    bpost.set_chargeable_weight(round(bpost.chargeable_weight + (-1 * dif), 2))
                    dif_ch = dif_ch + dif
                else:
                    bpost.set_chargeable_weight(round(bpost.chargeable_weight + dif_ch, 2))
                    break
                i= i - 1
                bpost = box.bpost_list[i]
        i = -1
        bpost = box.bpost_list[i]
        if dif_am >0:
            bpost.set_amount(round(bpost.amount + dif_am, 2))
        else:
            while dif_am < 0:
                if dif_am + bpost.amount <= 0:
                    dif = bpost.amount - 0.2
                    bpost.set_amount(round(bpost.amount + (-1 * dif), 2))
                else:
                    bpost.set_amount(round(bpost.amount + dif_am, 2))
                    i = i - 1
                    bpost = box.bpost_list[i]
'''
    '''total_ch,total_am = 0,0
    for box in box_list:
        for bpost in box.bpost_list:
            total_ch = total_ch + bpost.chargeable_weight
            total_am = total_am + bpost.amount
    if total_ch != round(float(invoice_data_map['chargeable_weight']), 2):
        dif_ch = round(round(float(invoice_data_map['chargeable_weight']), 2) - total_ch, 2)
        bpost.set_chargeable_weight(round(bpost.chargeable_weight + dif_ch, 2))
    if total_am != round(float(invoice_data_map['invoice_amount']), 2):
        dif_am = round(round(float(invoice_data_map['invoice_amount']), 2) - total_am, 2)
        bpost.set_amount(round(bpost.amount + dif_am, 2))'''


def calc_chargeable_weight(box):
    box_sum_weight = box.calc_box_weight()
    temp = round(box.chargeable_weight / box_sum_weight,2)
    for bpost in box.bpost_list:
        res = round(temp * bpost.weight, 2)
        bpost.set_chargeable_weight(res)

def calc_amount(kg_charge, box):
    for bpost in box.bpost_list:
        bpost.set_amount(round(bpost.chargeable_weight * kg_charge, 2))

def calc_amount_fbg( box_list):
    for box in box_list:
        for bpost in box.bpost_list:
         bpost.set_amount(math.floor((float(invoice_data_map['invoice_amount'])/float(invoice_data_map['number_of_bposts']) *100))/100.0)

def start():
    global continue_flag
    box_list = []
    error.set('')
    if len(df_list) <= 0:
        error.set("please enter at least one delivery file")
    else:
        file_name = invoice_data_map['invoice_number'] + '.csv'
        create_csv_file(file_name)
        print(df_list)
        for df in df_list:
            payload = {}
            headers = {}
            data = get_data_from_service(headers, payload, url,df)
            process_df_data(data,box_list)
            #tk.Label(frame, text='success',font = title_font_style).grid(row=0)
            #frame.pack(side= 'top', anchor='nw')

        if invoice_data_map['supplier_code'] == 'FBG':
            calc_amount_fbg(box_list)
            calc_chargeable_fbg(box_list)
        dif_am, dif_ch = get_chargeable_weight_amount_dif(box_list)
        create_dif_screen(dif_am, dif_ch, box_list, file_name)





def calc_chargeable_fbg(box_list):
    for box in box_list:
        for bpost in box.bpost_list:
         bpost.set_chargeable_weight(bpost.weight)


def continue_proccess(box_list, file_name):
    if invoice_data_map['supplier_code'] == 'FBG':
        fix_amount_fbg(box_list)
    else:
        fix_chargeable_weight_amount(box_list)
    write_data_to_csv(box_list, file_name)
    convert_csv_to_text(file_name)
    move_file_to_ftp(file_name.split('.')[0] + '.text')
    delete_file(file_name.split('.')[0] + '.text')
    exit_screen()
    main()

def exit_screen():
    global continue_flag
    clear_frame()
    continue_flag = True
    r.quit()

def create_dif_screen(dif_am, dif_ch, box_list, file_name):
    clear_frame()
    tk.Label(frame, text='amount and weight differences:', font = title_font_style).grid(row=0, columnspan=1)
    tk.Label(frame, text='amount:', font = regular_font_style).grid(row=1, columnspan=1, pady=(10, 20))
    tk.Label(frame, text='weight:', font=regular_font_style).grid(row=2, columnspan=1, pady=(10, 20))
    tk.Label(frame, text='number of bposts from delivery:', font=regular_font_style).grid(row=3, columnspan=1, pady=(10, 20))
    tk.Label(frame, textvariable = error,font = error_font_style,fg='red').grid(row=19,pady=(5, 5))
    tk.Button(frame, text='exit', fg='blue', command=lambda: exit_screen()).grid(row=20, column=0,pady=(10, 5))
    tk.Button(frame, text='continue', fg='blue', command=lambda: continue_proccess(box_list, file_name)).grid(row=20, column=1,pady=(10,5))
    tk.Label(frame, text=str(dif_am), font=regular_font_style).grid(row=1, column=1)
    tk.Label(frame, text=str(dif_ch), font=regular_font_style).grid(row=2, column=1)
    tk.Label(frame, text=str(calculate_number_of_bposts(box_list)), font=regular_font_style).grid(row=3, column=1)
    frame.pack(side=tk.TOP, anchor=tk.NW)
    frame.pack_propagate(0)

def calculate_number_of_bposts(box_list):
    count = 0
    for box in box_list:
        count = count + len(box.bpost_list)
    return count



def add_delevery_file():
    error.set('')
    df = delivery_file.get()
    if df == '':
        error.set("please enter a valid delivery file")
    else:
        df_list.append(df)
        delivery_file.set('')
        lb = tk.Label(frame, text=str(len(df_list)) + ')  ' + df, font= regular_font_style,anchor="w").\
            grid(row=2 + len(df_list),column = 0)

def create_delivery_file_win(files):
    if invoice_data_map['supplier_code'] !='FBG':
        tk.Label(frame, text='invoice Total Amount Calculation:                       ', font = title_font_style).grid(row=0, columnspan=5)
        tk.Label(frame, text='Total Amount USD: '+ invoice_data_map['invoice_amount'] , font=regular_font_style).grid(row=1, columnspan=1)
        tk.Label(frame, text='vat USD: ' + invoice_data_map['vat_usd'] , font=regular_font_style).grid(row=2, columnspan=1)
        tk.Label(frame, text='Dollar Exchange Rate: ' + invoice_data_map['dollar_exchange_rate'] , font=regular_font_style).grid(row=3, columnspan=1)
        tk.Label(frame, text='',font=title_font_style).grid(row=4, columnspan=5)
    tk.Label(frame, text='delivery files found for tkr: ' + invoice_data_map["tracking_number"] +'           ', font = title_font_style).grid(row=5, columnspan=5)
    i = 6
    for delivery in files:
        tk.Label(frame, text=str(delivery['DeliveryID']) + ' with ' + str(delivery['numberOfBposts']) + ' Bposts in '+
                 str(delivery['numberOfBoxes']) +' boxes',
                 font=regular_font_style).grid(row=i ,columnspan=1)
        i = i + 1
    i +=1
    tk.Button(frame, text='START', fg='blue', command=lambda: start()).grid(row=i + 3, column=0,pady=(10,5))
    frame.pack(side=tk.TOP, anchor=tk.NW)
    frame.pack_propagate(0)



def create_delivery_file_window():
    tk.Label(frame, text='add delivery files:', font = title_font_style).grid(row=0, columnspan=1)
    tk.Label(frame, text='delivery file:', font = regular_font_style).grid(row=1, columnspan=1, pady=(10, 20))
    tk.Label(frame, textvariable = error,font = error_font_style,fg='red').grid(row=19,pady=(5, 5))
    tk.Button(frame, text='ADD', fg='blue', command=lambda: add_delevery_file()).grid(row=20, column=0,pady=(10, 5))
    tk.Button(frame, text='START', fg='blue', command=lambda: start()).grid(row=20, column=1,pady=(10,5))
    tk.Entry(frame, textvariable=delivery_file).grid(row=1, column=1)
    frame.pack(side=tk.TOP, anchor=tk.NW)
    frame.pack_propagate(0)


def update_supplier_info():
    supplier =  invoice_data_map['supplier_code'].get()
    if supplier == 'UPS':
        invoice_data_map['charge_type'].set("FLR")
        invoice_data_map['supplier'].set('UPS')
    elif supplier == 'DSV':
        invoice_data_map['charge_type'].set("FLR")
        invoice_data_map['supplier'].set('DSV')
    elif supplier == 'FBG':
        invoice_data_map['charge_type'].set("CUC")
        invoice_data_map['supplier'].set('FBG')
    elif supplier == 'DHL':
        invoice_data_map['charge_type'].set("FLR")
        invoice_data_map['supplier'].set('DHL')
    clear_frame()
    create_invoice_window()
    error.set('')
    r.mainloop()

def reload_test():
    if test_mode.get()==1:
        invoice_data_map['supplier'].set(config[invoice_data_map['supplier_code'].get()]['supplier'])
        invoice_data_map['operational_number'].set(config[invoice_data_map['supplier_code'].get()]['supplier_ref'])
        invoice_data_map['supplier_code'].set(config[invoice_data_map['supplier_code'].get()]['supplier_code'])
        invoice_data_map['invoice_number'].set(config[invoice_data_map['supplier_code'].get()]['invoice_number'])
        invoice_data_map['invoice_date'].set(config[invoice_data_map['supplier_code'].get()]['invoice_date'])
        invoice_data_map['vat'].set(config[invoice_data_map['supplier_code'].get()]['vat_nis'])
        invoice_data_map['air_trans_nis'].set(config[invoice_data_map['supplier_code'].get()]['air_trans_nis'])
        invoice_data_map['air_trans_usd'].set(config[invoice_data_map['supplier_code'].get()]['air_trans_usd'])
        invoice_data_map['tracking_number'].set(config[invoice_data_map['supplier_code'].get()]['track_number'])
        invoice_data_map['chargeable_weight'].set(config[invoice_data_map['supplier_code'].get()]['chg_weight'])
        invoice_data_map['invoice_amount_nis'].set(config[invoice_data_map['supplier_code'].get()]['invoice_amount_nis'])

    frame.pack(side=tk.TOP, anchor=tk.NW)
    frame.pack_propagate(0)

def create_invoice_window():
    global test_mode 
    test_mode = tk.IntVar()
    global first_flag
    tk.Label(frame, text='enter invoice details:', font=title_font_style).grid(row=0, pady=(2, 5), columnspan=1)
    lb = tk.Label(frame, text='Supplier:',font = regular_font_style).grid(row=2, pady=10, )
    tk.Label(frame, text='Supplier Code:',font = regular_font_style).grid(row=1, pady=10)
    tk.Label(frame, text='Invoice Number:',font = regular_font_style).grid(row=4,  pady=10)
    tk.Label(frame, text='Invoice Date:',font = regular_font_style).grid(row=5,  pady=10)
    tk.Label(frame, text='Supplier Reference:',font = regular_font_style).grid(row=3,  pady=10)
    tk.Label(frame, text='Chargeable Weight:',font = regular_font_style).grid(row=8,  pady=10)
    tk.Label(frame, text='Number Of Bposts:', font=regular_font_style).grid(row=9, pady=10)
    tk.Label(frame, text='Charge Type:',font = regular_font_style).grid(row=10,  pady=10)
    tk.Label(frame, text='Tracking Number:',font = regular_font_style).grid(row=11,  pady=10)
    if invoice_data_map['supplier'].get() =='UPS' or invoice_data_map['supplier'].get() == 'DSV':
        tk.Label(frame, text='Invoice Amount NIS:', font=regular_font_style).grid(row=7, pady=10)
        tk.Label(frame, text='VAT NIS:', font=regular_font_style).grid(row=6, pady=10)
        tk.Label(frame, text='Air Transport NIS:', font=regular_font_style).grid(row=12, pady=10)
        tk.Label(frame, text='Air Transport USD:', font=regular_font_style).grid(row=13, pady=10)
        tk.Entry(frame, textvariable=invoice_data_map['vat']).grid(row=6, column=1, padx=(15, 0))
        tk.Entry(frame, textvariable=invoice_data_map['invoice_amount_nis']).grid(row=7, column=1, padx=(15, 0))
        tk.Entry(frame, textvariable=invoice_data_map['air_trans_nis']).grid(row=12, column=1, padx=(15, 0))
        tk.Entry(frame, textvariable=invoice_data_map['air_trans_usd']).grid(row=13, column=1, padx=(15, 0))
        if test_mode==1:
            invoice_data_map['vat'].set('45')
        # tk.Entry(frame, textvariable=tk.StringVar(r,'207.98')).grid(row=6, column=1, padx=(15, 0))
        # tk.Entry(frame, textvariable=invoice_data_map['invoice_amount_nis']).grid(row=7, column=1, padx=(15, 0))
        # tk.Entry(frame, textvariable=invoice_data_map['air_trans_nis']).grid(row=12, column=1, padx=(15, 0))
        # tk.Entry(frame, textvariable=invoice_data_map['air_trans_usd']).grid(row=13, column=1, padx=(15, 0))

    else:
        tk.Label(frame, text='Invoice Amount:', font=regular_font_style).grid(row=7, pady=10)
        tk.Label(frame, text='Currency:', font=regular_font_style).grid(row=6, pady=10)
        tk.Entry(frame, textvariable=invoice_data_map['currency']).grid(row=6, column=1, padx=(15, 0))
        tk.Entry(frame, textvariable=invoice_data_map['invoice_amount']).grid(row=7, column=1, padx=(15, 0))
        
    if invoice_data_map['supplier_code'].get() == '' or invoice_data_map['supplier_code'].get() == 'FBG':
        invoice_data_map['charge_type'].set("CUC")
        invoice_data_map['supplier_code'].set('FBG')
        invoice_data_map['supplier'].set('FBG')
        invoice_data_map['currency'].set('USD')
    tk.OptionMenu(frame, invoice_data_map['charge_type'], "FLR", "CUC").grid(row=10,  column= 1,pady=(8,0))
    tk.Label(frame, textvariable = error,font = error_font_style,fg='red').grid(row=14,  pady=5)
    tk.Button(frame, text='OK', fg='blue', command = lambda:  handel_invocie_data()).grid(row=15,column = 1,columnspan=2,pady=(0,5))
    tk.Entry(frame, textvariable = invoice_data_map['supplier']).grid(row=2, column=1, padx=(15,0), columnspan=3)
    tk.Entry(frame, textvariable=invoice_data_map['operational_number']).grid(row=3, column=1, padx=(15, 0))
    tk.OptionMenu(frame, invoice_data_map['supplier_code'],'UPS','FBG','DSV', command = lambda  x=None: update_supplier_info()).grid(row=1, column=1,padx=(15,0))
    tk.Entry(frame, textvariable = invoice_data_map['invoice_number']).grid(row=4, column=1,padx=(15,0))
    tk.Entry(frame, textvariable = invoice_data_map['invoice_date']).grid(row=5, column=1,padx=(15,0))
    tk.Entry(frame, textvariable=invoice_data_map['chargeable_weight']).grid(row=8, column=1, padx=(15, 0))
    tk.Entry(frame, textvariable=invoice_data_map['number_of_bposts']).grid(row=9, column=1, padx=(15, 0))
    tk.Entry(frame, textvariable=invoice_data_map['tracking_number']).grid(row=11, column=1, padx=(15, 0))
    # test_btn = tk.Button(frame, text='Test Mode', fg='blue', command = lambda:toggle(test_btn)).grid(row=2,column = 25,columnspan=2,pady=(0,5))
    tk.Checkbutton(frame, text='Test Mode',variable=test_mode, onvalue=1, offvalue=0,command=reload_test).grid(row=1, column=550, padx=(15, 0))
    if first_flag:
        first_flag = False
    else:
        error.set("Last invoice was successfully uploaded")
    frame.pack(side=tk.TOP, anchor=tk.NW)
    frame.pack_propagate(0)


def next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"


def main():

    global continue_flag
    global first_flag
    try:
        continue_flag = True
        while continue_flag:
            continue_flag = False
            initialize()
            create_invoice_window()
            r.geometry("600x700")
            r.bind_class("Entry", "<Down>", next_widget)
            r.title('invoice and delivery file window')
            r.mainloop()
            time.sleep(1)
            first_flag = False
            df_list.clear()
    except Exception  as e:
        abort(str(e))



if __name__ == '__main__':
    main()