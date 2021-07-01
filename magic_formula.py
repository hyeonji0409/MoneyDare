import xlrd
import pandas as pd

# df = pd.read_ex

file_path = 'magic_formula_data.xlsx'
wd = xlrd.open_workbook(file_path)

pbr_sh = wd.sheet_by_name('PBR')

#'pbr' 순위 구하기. 양수 값의 데이터만 필요 & pbr값 작을수록 좋음
pbr_dict = {}

for i in range(1, pbr_sh.nrows):
    data = pbr_sh.row_values(i)
    name = data[0]
    pbr = data[1]
    if pbr > 0:
        pbr_dict[name] = pbr

import operator

sorted_pbr = sorted(pbr_dict.items(),key=operator.itemgetter(1))

#pbr 순위 지정
pbr_rank = {}

for num, firm in enumerate(sorted_pbr):
    pbr_rank[firm[0]] = num + 1

#GP_A  순위 구하기. 값이 존재하는 데이터만 필요 & GP_A 값 클 수록 좋음
gp_a_sh = wd.sheet_by_name('GP_A')

gp_a_dict = {}

for j in range(1, gp_a_sh.nrows):
    data = gp_a_sh.row_values(j)
    name = data[0]
    gp_a = data[1]
    if gp_a != 0:
        gp_a_dict[name] = gp_a

sorted_gp_a = sorted(gp_a_dict.items(), key=operator.itemgetter(1), reverse=True)

gp_a_rank = {}
for num, firm in enumerate(sorted_gp_a):
    gp_a_rank[firm[0]] = num + 1

total_rank = {}

for name in gp_a_rank.keys():
    if name in pbr_rank.keys():
        total_rank[name] = pbr_rank[name] + gp_a_rank[name]

#total_rank의 value 값을 기준키로 하여 total_rank를 오르차순으로 저장. value값이 작은 순서대로 정렬
sorted_total = sorted(total_rank.items(), key=operator.itemgetter(1))

magic_rank = {}

for num, firm in enumerate(sorted_total):
    magic_rank[firm[0]] = num +1


sorted_magic = sorted(magic_rank.items(), key=operator.itemgetter(1))

print(sorted_magic[:20])


df = pd.DataFrame.from_records(sorted_magic[:20])
df.to_excel('magic.xlsx')



