import psycopg2
import psycopg2.extras
from x5t_connect import db_request


class Driver:
    dr_req = """select * from "core-drivers-schema".drivers where number = '{0}'"""
    pl_req = """select * from "core-waybills-schema".waybills where system_status = 'I0070' and user_status = 'E0002' and 
    _type ='SAP' and driver_number = '{0}' order by user_status asc """
    inv_req = """select * from "core-invoices-schema".own_trip where waybillid = '{0}'"""

    def __init__(self, tab_num: int, ):
        self.tab_num = tab_num
        self.card = db_request(self.dr_req.format(str(self.tab_num).zfill(8)))[0]
        self.pl = db_request(self.pl_req.format(self.card['number']))

        if not self.pl:
            self.invoices = []
        else:
            self.invoices = db_request(self.inv_req.format(self.pl[0]['number']))

        #print(self.pl_req.format(self.driver['number']))


driver = Driver(1440687)


print(driver.card)
print(driver.pl)
for i in driver.invoices: print(i)

