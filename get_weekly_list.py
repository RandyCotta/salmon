#!/usr/bin/python


#this is some change to this file...

import os
import xlrd
import csv

def csv_from_excel():
    
    os.system('wget http://www.cboe.com/publish/weelkysmf/weeklysmf.xls')
    wb = xlrd.open_workbook('weeklysmf.xls')
    sh = wb.sheet_by_name('Sheet1')
    your_csv_file = open('./new_weeklies.csv', 'wb')
    wr = csv.writer(your_csv_file)

    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()

    os.system(''' cat new_weeklies.csv |sed 's/\,\ /\ /g'|sed 's/\"//g'|awk -F',' 'NF==13 {print $1,$4}'|grep Equity|awk '{print $1}'|sort|uniq > wkly_equity_symbols.txt ''')

    os.system('rm -f new_weeklies.csv')
    os.system('rm -f weeklysmf.xls*')

if __name__=="__main__":

    csv_from_excel()
