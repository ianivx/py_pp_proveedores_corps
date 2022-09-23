from utils.utils import *
from datetime import datetime

proveedores_row = {
    "Bloqueo de pago":"",
    "Cuenta":5276,
    "Nit de Proveedor": "76014610-2",
    "Nombre del Proveedor": "LG ELECTRONICS INC. CHILE LTDA.",
    "Nit de Cliente": "",
    "Nombre de Cliente": "",
    "Nº documento": "1901252459",
    "Clase de documento": "K1",
    "Referencia": "365428",
    "Fecha de documento": "17-06-22",
    "Vencimiento neto": datetime.strptime("22-08-22", '%d-%m-%y'),
    "Importe en moneda local": "-404.993",
    "Moneda del documento": "CLP",
    "Texto": "SUC:10056|OC:11376988|DIF:0|FR:180622",
    "Fecha compensación": "",
    "Operación referencia": "BKPFF",	
    "Doc.compensación": "",
    "Asignación": "PR005XEPELIN250822"
}

def test_get_fecha_de_pago_real_proveedor_with_past_date():
    today = datetime.strptime("25-08-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "12-09-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_below_corte_inferior_1():
    proveedores_row["Vencimiento neto"] = datetime.strptime("01-11-22", '%d-%m-%y')
    today = datetime.strptime("31-10-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "25-11-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_below_corte_inferior_2():
    proveedores_row["Vencimiento neto"] = datetime.strptime("08-11-22", '%d-%m-%y')
    today = datetime.strptime("31-10-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "25-11-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_below_corte_inferior_3():
    proveedores_row["Vencimiento neto"] = datetime.strptime("15-11-22", '%d-%m-%y')
    today = datetime.strptime("31-10-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "25-11-2022"

# eliminar con la actualizacion
def test_get_fecha_de_pago_real_proveedor_with_future_date_in_between_cortes():
    proveedores_row["Vencimiento neto"] = datetime.strptime("08-11-22", '%d-%m-%y')
    today = datetime.strptime("01-11-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "25-11-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_above_corte_superior_1():
    proveedores_row["Vencimiento neto"] = datetime.strptime("16-11-22", '%d-%m-%y')
    today = datetime.strptime("01-11-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "12-12-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_above_corte_superior_2():
    proveedores_row["Vencimiento neto"] = datetime.strptime("30-11-22", '%d-%m-%y')
    today = datetime.strptime("01-11-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "12-12-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_above_corte_superior_3():
    proveedores_row["Vencimiento neto"] = datetime.strptime("31-10-22", '%d-%m-%y')
    today = datetime.strptime("01-10-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "10-11-2022"

def test_get_fecha_de_pago_real_proveedor_with_future_date_between_years():
    proveedores_row["Vencimiento neto"] = datetime.strptime("25-12-22", '%d-%m-%y')
    today = datetime.strptime("01-12-22", '%d-%m-%y')
    fecha_de_pago = get_fecha_de_pago_real_proveedor(proveedores_row, today)
    assert fecha_de_pago == "10-01-2023"