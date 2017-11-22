# check_gian.py
# created by Tanaka Takuma on 2017/11/03
# -*- coding: utf-8 -*-

import re
import nkf
import csv
import sys
import database
import os

def Search_bills(db, name, year, bills): 
    sql = "select HATSUGEN from %s where KAISAI_NEN = %s;" % (name, str(year))
    rows = db.GetSQLRows(sql)
    find_list = []
    for r in rows:
        for bill in bills:
            if bill in r[0]:
                find_list.append(bill) #発言で見つかった議案を収納
    return list(set(find_list)) #重複を削除

if __name__ == "__main__":
    path = "/home/t-tanaka/Documents/gian/"
    csv_list = os.listdir(path)
    for csv_file in csv_list:
        if csv_file[0] == ".":
            continue
        f = open(path + csv_file[:-4] + '.csv', 'rt')
        bills = csv.reader(f, delimiter=',')
        tname = ""
        # 各年度毎に議案リストを分ける
        h24 = []
        h25 = []
        h26 = []
        for bill in bills:
            tname = bill[0]
            match = re.match(r".*平成([0-9０-９]+)年.*", bill[1].replace("　", "").replace(" ", ""))
            if match is None:
                print("--------------miss-------------")
                print(bill[1])
            elif bill[4] == "知事提出議案":
                num = int(match.group(1))
                if num == 24:
                    h24.append(bill[3].strip())
                elif num == 25:
                    h25.append(bill)
                elif num == 26:
                    h26.append(bill)
                    
        db = database.Database()
        #db.Connect_Database("discuss_honkaigi_splited")
        db.Connect_Database("47honkaigi")
        sql = "show tables;"
        table_list = db.GetSQLRows(sql)
        tablen = ""
        for table in table_list:
            if csv_file[:-4] in table[0]:
                tablen = table[0]
                break
        

        #各年度ごとで議事録から議案を検索，見つかった議案をリストで取得
        c24 = Search_bills(db, tablen, 24, h24)
        #c25 = Search_bills(db, args[1], 25, h25)
        #c26 = Search_bills(db, args[1], 26, h26)
        #print(len(h24), len(h25), len(h26))
        #print(len(c24), len(c25), len(c26))
        n24 = []
        for h in h24:
            n24.append(h)
        for h in h24:
            for c in c24:
                if h == c:
                    n24.remove(h)
        #print(tname+","+str(len(h24))+","+str(len(c24))+","+str(len(n24)))
        print(c24)
        for n in n24:
            if csv_file[:-4] == "akita":
                print(n)
        f.close()
        db.Close_Database()
