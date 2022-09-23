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

def test_is_fin_de_semana_true():
    fecha_sabado = "24-09-2022"
    assert is_fin_de_semana(fecha_sabado) == True

def test_is_fin_de_semana_false():
    fecha_viernes = "23-09-2022"
    assert is_fin_de_semana(fecha_viernes) == False


def test_is_feriado_true():
    fecha_fiestas_patrias = "18-09-2022"
    assert is_feriado(fecha_fiestas_patrias) == True

def test_is_feriado_false():
    fecha_cumpleaños = "28-11-2022"
    assert is_feriado(fecha_cumpleaños) == False

def test_get_next_lunes():
    fecha_viernes = "23-09-2022" 
    next_lunes = get_next_lunes(fecha_viernes)
    assert next_lunes == "26-09-2022"

def test_get_next_lunes_between_years():
    ultimo_dia = "31-12-2022"
    next_lunes = get_next_lunes(ultimo_dia)
    assert next_lunes == "02-01-2023"

def test_get_next_dia():
    feriado_fiestas_patrias = "18-10-2022"
    next_dia = get_next_dia(feriado_fiestas_patrias)
    assert next_dia == "19-10-2022"

def test_check_if_dia_is_habil_feriado():
    feriado_fiestas_patrias = "18-09-2022"
    next_dia = check_if_dia_is_habil(feriado_fiestas_patrias)
    assert next_dia == "20-09-2022"

def test_check_if_dia_is_habil_workday():
    feriado_fiestas_patrias = "21-09-2022"
    next_dia = check_if_dia_is_habil(feriado_fiestas_patrias)
    assert next_dia == "21-09-2022"

def test_check_if_dia_is_habil_weekend():
    feriado_fiestas_patrias = "24-09-2022"
    next_dia = check_if_dia_is_habil(feriado_fiestas_patrias)
    assert next_dia == "26-09-2022"
