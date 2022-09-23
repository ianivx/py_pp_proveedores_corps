import requests
from datetime import date, datetime, timedelta
from pprint import pprint
import collections

def get_feriados_string_list():
    x = requests.get('https://api.victorsanmartin.com/feriados/en.json')
    response = x.json()
    feriados_object_list = response['data']
    feriados_date_list = []
    for feriado_object in feriados_object_list:
        feriado_string = feriado_object['date']
        feriado_date_object = datetime.strptime(feriado_string, "%Y-%m-%d").date()
        feriados_date_list.append(feriado_date_object)
    feriados_string_list = list(map(lambda x: x.strftime('%d-%m-%Y'), feriados_date_list))
    return feriados_string_list

feriados_string_list = get_feriados_string_list()


# make request to feriados api
def is_feriado(fecha):
    return(fecha in feriados_string_list)

def is_fin_de_semana(fecha):
    weekday = datetime.strptime(fecha, "%d-%m-%Y").weekday()
    return(weekday == 5 or weekday == 6)

def get_next_lunes(fecha):
    fecha = datetime.strptime(fecha, "%d-%m-%Y")
    next_lunes = fecha + timedelta(days=-fecha.weekday(), weeks=1)
    return next_lunes.strftime("%d-%m-%Y")

def get_next_viernes(fecha):
    fecha = datetime.strptime(fecha, "%d-%m-%Y")
    next_viernes = fecha + timedelta( (4-fecha.weekday()) % 7 )
    return next_viernes.strftime("%d-%m-%Y")

def get_next_dia(fecha):
    fecha = datetime.strptime(fecha, "%d-%m-%Y")
    return (fecha + timedelta(days=1)).strftime("%d-%m-%Y")

def check_if_dia_is_habil(fecha):
    new_fecha = fecha
    if(is_fin_de_semana(fecha)):
        new_fecha = get_next_lunes(fecha)
    while(is_feriado(new_fecha)):
        new_fecha = get_next_dia(new_fecha)
    return new_fecha


def get_next_available_friday(this_date):
    this_date = this_date.strftime("%d-%m-%Y")
    next_available_friday = get_next_viernes(this_date)
    while(is_feriado(next_available_friday)):
        next_available_friday = get_next_dia(next_available_friday)
    return next_available_friday

def get_next_supplier_available_payment_date(this_date):
    day = this_date.day
    month = this_date.month
    year = this_date.year
    if(day <= 7):
        next_payment_date = datetime(year, month%12, 10).strftime("%d-%m-%Y")
        
    elif(day > 7 and day <= 22):
        next_payment_date = datetime(year, month%12, 25).strftime("%d-%m-%Y")
    elif(day > 22):
        next_payment_date = datetime(year, (month+1)%12, 10).strftime("%d-%m-%Y")
    next_payment_date = check_if_dia_is_habil(next_payment_date)
    return next_payment_date 


def get_fecha_de_pago_real_pyme(row):
    fecha_de_pago_real = ''
    fecha_vencimiento = row["Vencimiento neto"]
    day = fecha_vencimiento.day
    month = fecha_vencimiento.month
    year = fecha_vencimiento.year
    today = datetime.today()
    if(today > fecha_vencimiento):
        return get_next_available_friday(today)
    else:
        fecha_vencimiento = datetime(year, month, day).strftime("%d-%m-%Y")
        fecha_de_pago_real = get_next_viernes(fecha_vencimiento)
        while(is_feriado(fecha_de_pago_real)):
            fecha_de_pago_real = get_next_dia(fecha_de_pago_real)
        return fecha_de_pago_real

def get_fecha_de_pago_real_proveedor(row, today):
    fecha_de_pago_real = ''
    fecha_vencimiento = row["Vencimiento neto"]
    day = fecha_vencimiento.day
    month = fecha_vencimiento.month
    year = fecha_vencimiento.year
    #first_fecha_de_corte_de_vencimiento =
    #second_fecha_de_corte_de_vencimiento =
    #TODO check clase de documento. if clase de documento is DD/SA/KV return '-'. Else continue with logic
    if(today > fecha_vencimiento):
        return get_next_supplier_available_payment_date(today)
    else:
        if(day >= 1 and day <= 15):
            fecha_de_pago_real = datetime(year, month%12, 25).strftime("%d-%m-%Y")
        elif(day >= 16 and day <= 31):
            new_month = (month)%12 + 1
            fecha_de_pago_real = datetime(year, new_month, 10).strftime("%d-%m-%Y")
        fecha_de_pago_real = check_if_dia_is_habil(fecha_de_pago_real)
        return fecha_de_pago_real




def get_observacion_documentos(row):
    clase_de_documento = row['Clase de documento']
    if clase_de_documento in ['K1', 'K7', 'DO', 'KX']:
        return 'Se paga'
    else:
        return 'Se descuenta'


def update_resumen_proveedor(resumen_proveedor, is_pyme):
    pprint(resumen_proveedor)
    new_resumen_proveedor = {}
    se_paga_from_past_date = 0
    se_descuenta_from_past_date = 0
    today = date.today()
    resumen_proveedor = collections.OrderedDict(sorted(resumen_proveedor.items()))
    print('resumen_proveedores: ', resumen_proveedor)

    for fecha_de_pago, montos in resumen_proveedor.items():
        print('fecha_de_pago: ', fecha_de_pago)
        print('monto se paga: ', resumen_proveedor[f'{fecha_de_pago}']['se_paga'])
        print('monto se descuenta: ', resumen_proveedor[f'{fecha_de_pago}']['se_descuenta'])
        print('')
        
        fecha_de_pago_date_object = datetime.strptime(fecha_de_pago, "%Y-%m-%d").date()
        if(today > fecha_de_pago_date_object):
            print(f'{fecha_de_pago} is a past date (today is {today}). add amounts to the next one')
            se_paga_from_past_date += montos['se_paga']
            se_descuenta_from_past_date += montos['se_descuenta']
        else:
            fecha_de_pago_date_object = datetime.strptime(fecha_de_pago, '%Y-%m-%d').date()
            new_fecha_de_pago = fecha_de_pago_date_object.strftime('%d-%m-%Y')
            new_se_paga = resumen_proveedor[f'{fecha_de_pago}']['se_paga'] + se_paga_from_past_date
            new_se_descuenta = resumen_proveedor[f'{fecha_de_pago}']['se_descuenta'] + se_descuenta_from_past_date
            new_resumen_proveedor[f'{new_fecha_de_pago}'] = {
                'se_paga': new_se_paga,
                'se_descuenta': new_se_descuenta
            }
            se_paga_from_past_date = 0
            se_descuenta_from_past_date = 0
        print('new_resumen_proveedor: ')
        pprint(new_resumen_proveedor)
        print('')

    # if all fechas de pago are past date, we will have an empty new_presumen_proveedor dict
    # hence, we need to set the next fecha de pago from todays, based of the is_pyme flag. this is
    # going to be a unique fecha_de_pago: every payment is going to be done in this date
    is_new_resumen_proveedor_empty = not bool(new_resumen_proveedor)
    if(is_new_resumen_proveedor_empty):
        new_fecha_de_pago = get_next_payment_date_from_current_date(is_pyme)
        print('new_fecha_de_pago: ', new_fecha_de_pago)
        new_resumen_proveedor[f'{new_fecha_de_pago}'] = {
                'se_paga': se_paga_from_past_date,
                'se_descuenta': se_descuenta_from_past_date
            }
        

    print('new_resumen_proveedor after processing: ', new_resumen_proveedor)
    return new_resumen_proveedor

def get_next_payment_date_from_current_date(is_pyme):
    today = date.today()
    if(is_pyme):
        return get_next_available_friday(today)
    else: 
        return get_next_supplier_available_payment_date(today)