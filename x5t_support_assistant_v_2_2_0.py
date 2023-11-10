import PySimpleGUI as sg
import psycopg2
import psycopg2.extras


car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'";
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'";

assign_tab_layout = [[sg.Text('ТС'), sg.InputText(),sg.Text('Группа'), sg.InputText()],
    [sg.Checkbox('Аренда ТТ'), sg.Checkbox('Аренда Крафтер МФП'),
     sg.Checkbox('Аренда Крафтер УРАЛ'),sg.Checkbox('NULL')],
    [sg.Submit('Привязать'), sg.Cancel('Выход')],]

chkptr_tab_layout = [[sg.Text('Id_invoice'), sg.InputText()] ,[sg.Submit('Исправить'), sg.Cancel('Выход')]]

layout = [[sg.TabGroup([[sg.Tab('Привязка ТС', assign_tab_layout), sg.Tab('Авточекпоинтер', chkptr_tab_layout)]])], [sg.Output(size=(103, 15))]]

window = sg.Window('Костыли для Х5Т v2.1.0 by A.Dmitriev', layout)

def db_request(sql_request: str):
    dict_result = []
    conn = psycopg2.connect(dbname='mfp', user='anton_dmitriev',
                            password='PgVsMtcn@jd$AonUns', host='msk-dpro-psg044')
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql_request)
    conn.commit()
    try:
        ans = cur.fetchall()
        for row in ans:
            dict_result.append(dict(row))
        return dict_result

    except psycopg2.ProgrammingError:
        return None

    cur.close()
    conn.close()

total_insert = []

class Invoice:

    inv_req = "SELECT * from \"core-invoices-schema\".invoice where id = '{0}';"
    p_req = """SELECT * from "core-invoices-schema".invoice_unloading_points where invoice_id = '{0}' and invoice_system_version = '{1}' order by sequence"""
    plants_req = """select * FROM "core-plants-schema".plants where id = '{0}'"""
    points =[]
    plants = []

    def __init__(self, invoice_id: int) -> None:

        self.invoice = db_request(self.inv_req.format(str(invoice_id)))[0]
        self.points = db_request(self.p_req.format(str(invoice_id), str(self.invoice['system_version'])))
#            self.points.append(i['internal_point_id'])
        for i in self.points:
            self.plants.append(db_request(self.plants_req.format(i['internal_point_id'])))
 #       for plant in self.points: self.plants.append(db_request(self.plants_req.format()))



#        print(self.p_req.format(str(invoice_id), str(self.invoice['system_version'])))


def checkpoints_aio(invoice: Invoice) -> list:
    def insert_one_checkpoint(invoice: int, version: int, sequence: int, internal_point: str, external_point:str, stage_num: int) -> str:
        one_internal_stage = ('INSERT INTO "core-invoices-schema".driver_checkpoint '
                     '(invoice_id, invoice_version, invoice_point_sequence, internal_point_id, external_point_id,'
                     'stage_id, create_time, id, longitude, latitude, credentials, username)'
                     'VALUES     ({0}, {1}, {2}, \'{3}\', NULL, {4},now(), (select(max(id) + 1) FROM '
                     '"core-invoices-schema".driver_checkpoint),'
                     '0, 0, \'AUTOSET\', null);')

        one_external_stage = ('INSERT INTO "core-invoices-schema".driver_checkpoint '
                              '(invoice_id, invoice_version, invoice_point_sequence, internal_point_id, external_point_id,'
                              'stage_id, create_time, id, longitude, latitude, credentials, username)'
                              'VALUES     ({0}, {1}, {2}, NULL, \'{3}\', {4},now(), (select(max(id) + 1) FROM '
                              '"core-invoices-schema".driver_checkpoint),'
                              '0, 0, \'AUTOSET\', null);')

        if not external_point:
            return one_internal_stage.format(str(invoice), str(version), str(sequence), internal_point, str(stage_num))
        elif not internal_point:
            return one_external_stage.format(str(invoice), str(version), str(sequence), external_point, str(stage_num))
    result = []
    sequence = 0
    delete = """DELETE FROM "core-invoices-schema".driver_checkpoint where invoice_id = \'{0}\' ;""".format(str(invoice.invoice['id']))
    result.append(delete)

    for point in invoice.points:
        for stage in range(1, 5):
            result.append(insert_one_checkpoint(str(invoice.invoice['id']),
                                                str(invoice.invoice['system_version']),
                                                str(sequence), point['internal_point_id'], point['external_point_id'], str(stage),
                                                ))

        sequence += 1
    return result

def main():

    while True:                             # The Event Loop
        event, values = window.read()
        #print(event, values) #debug
        vehicle_code = group = None
        if event in (None, 'Exit', 'Выход'):
            break

        elif event == 'Привязать':

            if not values[0]:
                print('Отсутствует номер ТС.')

            else:
                vehicle_code = values[0].strip()
                if values[2] and not values[1] and not values[5] and not values[3] and not values[4]:
                    print(car_assign.format('Аренда ТТ', vehicle_code))
                    db_request(car_assign.format('Аренда ТТ', vehicle_code))

                elif values[3] and not values[1] and not values[2] and not values[4] and not values[5]:
                    print(car_assign.format('Аренда Крафтер МФП', vehicle_code))
                    db_request(car_assign.format('Аренда Крафтер МФП', vehicle_code))

                elif values[4] and not values[1] and not values[2] and not values[3] and not values[5]:
                    print(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))
                    db_request(car_assign.format('Аренда Крафтер УРАЛ', vehicle_code))

                elif values[5] and not values[1] and not values[2] and not values[3] and not values[4]:
                    print(car_drop.format(vehicle_code))
                    db_request(car_drop.format(vehicle_code))

                elif values[1]and not values[5] and not values[2] and not values[3] and not values[4]:
                    group = values[1].strip()
                    print(car_assign.format(group, vehicle_code))
                    db_request(car_assign.format(group, vehicle_code))

                else: print('Некорректный запрос!!!НЕЛЬЗЯ ПРИВЯЗАТЬ БОЛЕЕ ОДНОЙ ГРУППЫ!')

        if event == 'Исправить':

            if not values[6].strip():
                print('Введите номер рейса х5т')
            else:

                cur_invoice = Invoice(int(values[6].strip()))
                cure = checkpoints_aio(cur_invoice)

                for i in cure:
                    db_request(i)
                #print(i)

                print('Рейс {0} исправлен'.format(values[6]))


if __name__ == "__main__":
    main()