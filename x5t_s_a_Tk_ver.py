from tkinter import *
from tkinter import ttk, scrolledtext
import psycopg2
import psycopg2.extras
import logging

car_assign = "UPDATE \"core-vehicle-schema\".vehicle SET group_number='{0}' WHERE code = '{1}'";
car_drop = "UPDATE \"core-vehicle-schema\".vehicle SET group_number=NULL WHERE code = '{0}'";

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


def vehicle_counter(code: str) -> int:
    counter = "select count(*) from \"core-vehicle-schema\".vehicle where code = \'{0}\'"
    return db_request(counter.format(code))[0]['count']

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


def insrt(out: scrolledtext.ScrolledText):
    out.insert(INSERT, 'insert')

window = Tk()
window.title("x5t support assistant")
window.geometry('700x400')

out = scrolledtext.ScrolledText(window, width=90, height=20)

tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Привязка ТС')
tab_control.add(tab2, text='Авточекпоинтер')

v_lbl = Label(tab1, text='Номер ТС:')
v_lbl.grid(column=0, row=0)
veh = Entry(tab1, width=15)
veh.grid(column=1, row=0)
g_lbl = Label(tab1, text='Группа:')
g_lbl.grid(column=2, row=0)
gr = Entry(tab1, width=15)
gr.grid(column=3, row=0)

att_state = BooleanVar()
att = Checkbutton(tab1, text='Аренда ТТ', var=att_state)
att.grid(column=0, row=1)
akm_state = BooleanVar()
akm = Checkbutton(tab1, text='Аренда Крафтер МФП', var=akm_state)
akm.grid(column=1, row=1)
aku_state = BooleanVar()
aku = Checkbutton(tab1, text='Аренда Крафтер Урал', var=aku_state)
aku.grid(column=2, row=1)
nul_state = BooleanVar()
nul = Checkbutton(tab1, text='Отвязать', var=nul_state)
nul.grid(column=3, row=1)
upd = ttk.Button(tab1, text='Привязать', command=)
upd.grid(column=4, row=1)



inv_lbl = Label(tab2, text='Номер рейса х5т:')
inv_lbl.grid(column=0, row=0)
inv = Entry(tab2, width=15)
inv.grid(column=1, row=0)
inst = ttk.Button(tab2, text='Исправить', command=insrt(out))
inst.grid(column=2, row=0)

tab_control.pack(expand=1, fill='both')


out.pack()
window.mainloop()