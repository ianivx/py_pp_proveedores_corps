#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 00:39:58 2022

@author: ihojman
"""
from calendar import weekday
import pandas as pd
import requests
from datetime import date, datetime, timedelta
from pprint import pprint

#TODO
# make request to feriados api
def is_feriado(fecha):
    False

def is_fin_de_semana(fecha):
    weekday = datetime.strptime(fecha, "%d-%m-%Y").weekday()
    return(weekday == 5 or weekday == 6)

def get_next_lunes(fecha):
    fecha = datetime.strptime(fecha, "%d-%m-%Y")
    next_lunes = fecha + timedelta(days=-fecha.weekday(), weeks=1)
    return next_lunes.strftime("%d-%m-%Y")

def get_next_dia(fecha):
    return (fecha + timedelta(days=1)).strftime("%d-%m-%Y")

def check_if_dia_is_habil(fecha):
    new_fecha = fecha
    if(is_fin_de_semana(fecha)):
        new_fecha = get_next_lunes(fecha)
    while(is_feriado(new_fecha)):
        new_fecha = get_next_dia(new_fecha)
    return new_fecha



def get_fecha_de_pago_real(row):
    fecha_de_pago_real = ''
    fecha_vencimiento = row["Vencimiento neto"]
    day = fecha_vencimiento.day
    month = fecha_vencimiento.month
    year = fecha_vencimiento.year
    #TODO check clase de documento. if clase de documento is DD/SA/KV return '-'. Else continue with logic
    if(day <= 7):
        fecha_de_pago_real = datetime(year, month%12, 10).strftime("%d-%m-%Y")
        
    elif(day > 7 and day <= 22):
        fecha_de_pago_real = datetime(year, month%12, 25).strftime("%d-%m-%Y")
    elif(day > 22):
        fecha_de_pago_real = datetime(year, (month+1)%12, 10).strftime("%d-%m-%Y")
    fecha_de_pago_real = check_if_dia_is_habil(fecha_de_pago_real)
    return fecha_de_pago_real 


def get_observacion_documentos(row):
    clase_de_documento = row['Clase de documento']
    if clase_de_documento in ['K1', 'K7', 'DO', 'KX']:
        return 'Se paga'
    else:
        return 'Se descuenta'

current_year = date.today().year #para encontrar los feriados del año
facturas_proveedores_df = pd.read_excel('proveedores-raw.xlsx', index_col=0)
#response = r = requests.get('https://apis.digital.gob.cl/fl/feriados')
#feriados_object = response.json()
proveedores = facturas_proveedores_df['Nombre del Proveedor'].dropna().unique()
nit_list = facturas_proveedores_df['Nit de Proveedor'].dropna().unique()
#print(proveedores)
clientes = facturas_proveedores_df['Nombre de Cliente'].dropna().unique()
#print(clientes)

# set fecha de pago real
facturas_proveedores_df['FECHA DE PAGO REAL'] = facturas_proveedores_df.apply(get_fecha_de_pago_real, axis=1)
# set proper date format
facturas_proveedores_df['Fecha de documento'] = facturas_proveedores_df['Fecha de documento'].dt.strftime("%d-%m-%Y")
facturas_proveedores_df['Vencimiento neto'] = facturas_proveedores_df['Vencimiento neto'].dt.strftime("%d-%m-%Y")

# object key: proveedor name, value: object of objects with key:fecha_de_pago and value: se_paga, se_descuenta
resumen_proveedores = {}
# map to associate nit to a proveedor name
nit_nombre_proveedor_map = dict(zip(nit_list, proveedores))
proveedor_dataframe_list = []
for nit_proveedor in nit_list:
    resumen_provedor = {}
    # for each proveedor, filter dataframe with df.loc[df['Nombre del Proveedor'] == nombre_del_proveedor]
    proveedor_df = facturas_proveedores_df.loc[(facturas_proveedores_df['Nit de Proveedor'] == nit_proveedor) | (facturas_proveedores_df['Nit de Cliente'] == nit_proveedor)]
    proveedor_df = proveedor_df.reset_index()
    print(proveedor_df)
    # mark 'Se paga' or 'Se descuenta' in each row based on clase de documento
    proveedor_df['PLAZO'] = ""
    proveedor_df['OBSERVACIÓN DOCUMENTOS'] = proveedor_df.apply(get_observacion_documentos, axis=1)
    # get list of paying dates
    fecha_de_pago_list = proveedor_df['FECHA DE PAGO REAL'].dropna().unique()
    for fecha_de_pago in fecha_de_pago_list:
        resumen_provedor[f'{fecha_de_pago}'] = {
            'se_paga': 0,
            'se_descuenta': 0
        }
    # for each factura check if amount is 'se_paga' or 'se_descuenta'
    for index, row in proveedor_df.iterrows():
        fecha_de_pago_row = row['FECHA DE PAGO REAL']
        monto_factura = row['Importe en moneda local']
        if(get_observacion_documentos(row) == 'Se paga'):
            resumen_provedor[f'{fecha_de_pago_row}']['se_paga'] = resumen_provedor[f'{fecha_de_pago_row}']['se_paga'] + monto_factura
        else:
            resumen_provedor[f'{fecha_de_pago_row}']['se_descuenta'] = resumen_provedor[f'{fecha_de_pago_row}']['se_descuenta'] + monto_factura
    # print(proveedor_df)
    proveedor_dataframe_list.append(proveedor_df)
    resumen_proveedores[nit_nombre_proveedor_map[f'{nit_proveedor}']] = resumen_provedor


# merge proveedor dataframes into one df
proveedores_detail_df = pd.concat(proveedor_dataframe_list)

# create dataframe with summary table for each proveedor
proveedor_summary_dataframe_list = []
for proveedor, resumen_provedor in resumen_proveedores.items():
    empty_row = ['','', '', '']
    header_matrix = [empty_row, empty_row, [proveedor, '', '', ''], ['Vencimientos', 'Se paga', 'Se descuenta', 'Total']]
    new_rows_matrix = []
    monto_total_se_descuenta = 0
    for fecha_de_pago, montos in resumen_provedor.items():
        monto_total_se_descuenta += montos['se_descuenta']
        monto_se_descuenta= ''
        monto_se_paga = montos['se_paga']
        monto_total = monto_se_paga
        if(monto_se_paga != 0):
            new_row = [fecha_de_pago, monto_se_paga, monto_se_descuenta, -monto_total]
            new_rows_matrix.append(new_row)
    # set to first row (4th element) of summary monto total de descuento and new monto total
    new_rows_matrix[0][2] = monto_total_se_descuenta
    first_row_monto_se_paga = new_rows_matrix[0][1]
    first_row_monto_se_descuenta = new_rows_matrix[0][2]  
    new_rows_matrix[0][3] =(first_row_monto_se_paga - first_row_monto_se_descuenta)*-1


    proveedor_matrix = header_matrix + new_rows_matrix
    pprint(proveedor_matrix)
    # create dataframe with proveedor_matrix
    proveedor_summary_dataframe = pd.DataFrame(proveedor_matrix)
    proveedor_summary_dataframe_list.append(proveedor_summary_dataframe)

    
# merge sumary dataframes
summary_dataframe = pd.concat(proveedor_summary_dataframe_list)

# drop unneeded columns
unneeded_columns_list = ['Bloqueo de pago', 'Nombre del Proveedor', 'Nombre de Cliente','Clase de documento','Vencimiento neto','Moneda del documento', 'Texto', 'Fecha compensación', 'Operación referencia', 'Doc.compensación']
for unneeded_column in unneeded_columns_list:
    proveedores_detail_df.drop(unneeded_column, inplace=True, axis=1)

# add empty column to match ripley format
summary_dataframe.insert(0, "", "")
print('summary_dataframe[2]:',summary_dataframe[2])
print(summary_dataframe)
#summary_dataframe.to_excel('./resumen.xlsx', index=False)




dfs = {'Sheet1': proveedores_detail_df, 'Resumen': summary_dataframe}

writer = pd.ExcelWriter("Output Proveedores Xepelin.xlsx", engine='xlsxwriter')                
for sheetname, df in dfs.items():  # loop through `dict` of dataframes
    
    if(sheetname == 'Sheet1'):
        df.to_excel(writer, index=False, sheet_name=sheetname)
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        extra_width = 1
    else:
        df.to_excel(writer, index=False, sheet_name=sheetname,  header=False)
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        # get the clsx writer workbook and worksheet objects
        workbook = writer.book
        # Add your accountancy format
        format1 = workbook.add_format({'num_format': 42})

        # Set format without assigning column width for columns C and D
        worksheet.set_column('C:C', None, format1)
        worksheet.set_column('D:D', None, format1)
        worksheet.set_column('E:E', None, format1)
        extra_width = 5
    for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + extra_width  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width

# Close the pandas Excel Writer and output Excel File
writer.save()

