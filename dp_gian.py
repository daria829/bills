# dp_kgian.py
# created by Tanaka Takuma on 2017/11/03
# -*- coding: utf-8 -*-

import re
import nkf
import csv
import sys
import database
import os

# データベースから議案を完全一致検索
def Search_bills(db, name, year, bills): 
    sql = "select HATSUGEN from %s where KAISAI_NEN = %s;" % (name, str(year))
    rows = db.GetSQLRows(sql)
    find_list = []
    for r in rows:
        for bill in bills:
            if bill in r[0]:
                find_list.append(bill) #発言で見つかった議案を収納
    return list(set(find_list)) #重複を削除

# 議事録と議案リストを用いてDPマッチング
def DPmatch_bills(db, name, year, bills):
    sql = "select HATSUGEN from %s where KAISAI_NEN = %s;" % (name, str(year))
    rows = db.GetSQLRows(sql)
    min_dlist = []
    for r in rows:
        min_d = 1
        ddata = None
        for bill in bills:
            d = dpmatch(bill, r[0])
            if d < 1 and min_d > d:
                min_ddata = []
                min_ddata.extend([d, bill, r[0]])
                min_d = d
        if ddata is not None:
            print(min_ddata)
            min_dlist.append(min_ddata)
    return min_dlist

# ペナルティ
p1 = 3 
p2 = 1
# DPマッチング用のテーブル作成
def create_table(pattern, text):
    table = [[0 for i in range(len(text))] for j in range(len(pattern))]
    for i in range(len(pattern)):
        for j in range(len(text)):
            if pattern[i] == text[j]:
                table[i][j] = 0
            else:
                table[i][j] = p1 
    return table

# コストを計算，最小コストを返す
def cost(table, keyi, keyj): 
    base_cost = table[keyi][keyj]
    if keyi > 0 and keyj > 0:
        right_c = base_cost + p2
        right = right_c + table[keyi][keyj-1]
        down_c = base_cost + p2
        down = down_c + table[keyi-1][keyj]
        downright_c = base_cost
        downright = downright_c + table[keyi-1][keyj-1]
        c, out = compare(right, down, right_c, down_c)
        return compare(out, downright, c, downright_c)
    elif keyi > 0:
        down_c = base_cost + p2
        down = down_c + table[keyi-1][keyj]
        return down_c, down 
    elif keyj > 0:
        right_c = base_cost + p2
        right = right_c + table[keyi][keyj-1]
        return right_c, right
    else:
        return 0, base_cost

def compare(a, b, x, y):
    if a < b:
        return x, a
    else:
        return y, b

# 編集距離を計算
def calc_dis(table, pattern, text):
    for i in range(len(pattern)):
        for j in range(len(text)):
            c, out = cost(table, i, j)
            table[i][j] = out
    return table[len(pattern)-1][len(text)-1] / len(pattern)

def dpmatch(pattern, text):
    table = create_table(pattern, text)
    return calc_dis(table, pattern, text)

# 各年度毎に議案リストを分ける
def separate_bills(bills):
    h24 = []
    h25 = []
    h26 = []
    for bill in bills:
        name = bill[0]
        match = re.match(r".*平成([0-9０-９]+)年.*", bill[1].replace("　", "").replace(" ", ""))
        if match is None:
            pass
        elif bill[4] == "知事提出議案":
            num = int(match.group(1))
            if num == 24:
                h24.append(bill[3].strip())
            elif num == 25:
                h25.append(bill[3].strip())
            elif num == 26:
                h26.append(bill[3].strip())
    return name, h24, h25, h26
                
# ファイル名から適合するテーブルを検索
def search_table(db, filename):
    sql = "show tables;"
    table_list = db.GetSQLRows(sql)
    for table in table_list:
        if filename[:-4] in table[0]:
            return table[0]
            


if __name__ == "__main__":
    fc = open('dp.csv', 'w')
    csvWriter = csv.writer(fc, lineterminator='\n')
    path = "/home/t-tanaka/Documents/gian/"
    csv_list = os.listdir(path)
    db = database.Database()
    for csv_file in csv_list:
        if csv_file[0] == ".":
            continue
        if "iwate" not in csv_file:
            continue 
        f = open(path + csv_file[:-4] + '.csv', 'rt')
        bills = csv.reader(f, delimiter=',')
        name, h24, h25, h26 = separate_bills(bills) 
        #db.Connect_Database("discuss_honkaigi_splited")
        db.Connect_Database("47honkaigi")
        tablename = search_table(db, csv_file)
        c24 = DPmatch_bills(db, tablename, 24, h24)
        #csvファイルに出力
        for c in c24:
            c.insert(0, name)
            csvWriter.writerow(c)
                
        f.close()
    fc.close()
    db.Close_Database()
