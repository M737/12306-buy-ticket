import requests
import csv
import random
import warnings
import re
#忽略模块警告（证书警告）
warnings.filterwarnings("ignore")
def headers(from_,to_, date):
    #修改headers和cookie
    from_station = str(from_.encode('unicode-escape')).upper().lstrip("B'").rstrip("'").replace('\\\\','%') + '%2C'+ dic(from_)
    to_station = str(to_.encode('unicode-escape')).upper().lstrip("B'").rstrip("'").replace('\\\\','%') + '%2C'+ dic(to_)
    date = date
    herderlist = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12 ',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13',
        'Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 Safari/419.3',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ;  QIHU 360EE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; Maxthon/3.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; TencentTraveler 4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) )',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3'
        ]
    headers = {'Connection':'keep-alive',
        'Host':'kyfw.12306.cn',
        'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
        'Cookie':'JSESSIONID=36CB3F38EFB067D3D7FFCCB597F71194; \
         fp_ver=4.5.1; RAIL_EXPIRATION=1504394493584; \
         RAIL_DEVICEID=K1TVbnsaDmWGfKBYX8UFaKZF1L7v_uV0QMMFMi6hTrClpTvHI9oH2i1bGcdxxwsbl17dHFMR_scnAVAmmnc44xJjhUy8GuEzlxgvBjht8O2nBrG2RlrgMdIJ6RJ_F1QzotYE1-Ai-dJA_9BgYVNpHq4O22ywNS5d;\
         route=9036359bb8a8a461c164a04f8f50b252;\
         BIGipServerotn=535822858.24610.0000; \
         BIGipServerpool_passport=166527498.50215.0000; \
         _jc_save_fromStation=%s; \
         _jc_save_toStation=%s; \
         _jc_save_fromDate=%s; \
         _jc_save_toDate=2017-09-29; \
         _jc_save_wfdc_flag=dc' % (from_station,to_station,date),
        'User-Agent':random.choice(herderlist),
        'X-Requested-With':'XMLHttpRequest'
               }
    return headers
def need_input(from_station,to_station,train_date):
    params = {'leftTicketDTO.train_date':train_date,
            'leftTicketDTO.from_station':from_station ,
            'leftTicketDTO.to_station':to_station ,
            'purpose_codes':'ADULT'
             }
    return params
def get_datas():
    #站名校验
    while True:
        a = input('请输入起始站：')
        if dic(a):
            from_ = dic(a)
            break
        else:
            print('未查询到该站，请重新输入')
    while True:
        b = input('请输入目的站：')
        if dic(b):
            to_ = dic(b)
            break
        else:
            print('未查询到该站，请重新输入')
    #日期校验
    while True:
        input_date = input('请输入时间（格式如：2017-10-01）：')
        p = re.compile('^(?:(?!0000)[0-9]{4}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1[0-9]|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)-02-29)$')
        result = p.match(input_date)
        if result:
            date = result.group(0)
            break
        else:
            print('日期或者格式错误，请重新输入日期')
    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    res = requests.get(url, params=need_input(from_,to_,date), headers=headers(a,b,date), verify=False)
    if res.status_code == 200:
        return res, a, b, date
    elif res.status_code == 405:
        print('请输入正确的时间')
        return [],a, b, date
    else:
        print(res.status_code)
        return [],a, b, date
def data_analysis(res):
    try:
        datas = res.json()['data']['result']
        station = res.json()['data']['map']
        train_count = (len(datas))
        #print(datas[4].split('|'))
        items = []
        train_name_list = []
        for each in datas:
            item ={}
            data =each .split('|')
            # 是否可预订
            item['is_book'] = data[0]
            #当前状态
            item['status'] = data[1]
            #列车型号
            item['train_no'] = data[2]
            #列车编号
            item['train_name'] = data[3]
            #始发站与终点站
            item['train_from'] = data[4]
            item['train_to'] = data[5]
            #出发站与到达站
            item['from_station'] = data[6]
            item['to_station'] = data[7]
            #出发时间与到达时间
            item['time_from'] = data[8]
            item['time_to'] = data[9]
            #历时
            item['time_lasts'] = data[10]
            #站编号
            item['from_station_no'] = data[16]
            item['to_station_no'] = data[17]
            #列车座位类别
            item['soft_sleeper'] = data[23]
            item['no_seat'] = data[26]
            item['hard_sleeper']= data[28]
            item['hard_seat'] = data[29]
            item['business_seat'] = data[32]
            item['first_seat'] = data[31]
            item['second_seat'] = data[30]
            #列车类型
            item['seat_types'] = data[35]
            train_name_list.append(item['train_name'])
            items.append(item)
        return items, train_name_list
    except:
        return 

def dic(key):
    #站名编译
    dict_club={}
    with open('station.csv','r')as f:
        reader=csv.reader(f, delimiter=',')
        for row in reader:
            dict_club[row[0]]=row[1]
    if str(key) in dict_club :
        return dict_club[str(key)]
    else:
        return False
def rdic(vlues):
    #站名反编译
    dict_club={}
    with open('station.csv','r')as f:
        reader=csv.reader(f, delimiter=',')
        for row in reader:
            dict_club[row[1]]=row[0]
    return dict_club[str(vlues)]

def ticketprice(item,from_, to_, date):
    #获取价格
    try:
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'
        params = {'train_no':item['train_no'],
                'from_station_no':item['from_station_no'],
                'to_station_no': item['to_station_no'],
                'seat_types':item['seat_types'],
                'train_date':date
                 }
        res = requests.get(url, params=params, headers=headers(from_, to_, date), verify=False)
        res.encoding = 'utf-8'
        return res.json()['data']
    except:
        print('获取价格失败')
        return {}
def select(lis):
    for i in lis:
        yield i

def main():
    res, from_, to_, date = get_datas()
    if not res:
        return
    elif res.json()['messages']:
        print(res.json()['messages'][0])
        return
    elif not  res.json()['data']['result']:
        print('很抱歉，按您的查询条件，当前未找到%s 到 %s 的列车' % (from_, to_))
        return
    data,train_name_list = data_analysis(res)
    if not data:
        return
    print('共有%d列列车，分别是：\n %s' % (len(data), train_name_list),'\n')
    #可预定列车
    is_book = []
    for each in data:
        if not each['is_book'] == '': 
            is_book.append(each['train_name'])
    print('可预定%d列列车，分别是：\n %s ' % (len(is_book),is_book),'\n')
    p = re.compile("(^G\d{1,4})|(^D\d{1,4})")
    #区分普通列车和高铁动车
##    bullet_train_list = []
##    regular_train = []
##    for i in is_book:
##        if p.match(i):
##            bullet_train_list.append(i)
##        else:
##            regular_train.append(i)
    m = is_book.copy()
    for j in  m:
        lis = data[train_name_list.index(j)]
        if (lis['hard_seat'],lis['hard_sleeper'],lis['soft_sleeper']) ==(('无','无','无')or('无','无','')):
            is_book.remove(j)
    print('非无座的有%d列列车，分别是：\n %s'%(len(is_book),is_book))
  
    g = select(is_book)
    while True:
        while True:
            name = input('请输入所选列车（输入q/Q退出）：').upper()
            if name in train_name_list:
                break
            #退出机制
            elif name == 'Q':
                break
            elif name == '':
                try:
                    name = next(g)
                    break
                except StopIteration:
                    print('没有列车啦')
                    break
            else:
                print('所选列车不在备选列车中，请重新输入：')
        if name == 'Q':
            print("感谢您的使用")
            break
        elif name == '':
            pass
        else:
            item = data[train_name_list.index(name)]
            if item['status'] == '预订':
                price = (ticketprice(item,from_, to_, date))
                print(('列车：%s'+'\n'+'出发站：%s'+'\n'+'到达站：%s'+'\n'+'出发时间：%s'+'\n'+ \
                       '到达时间：%s'+'\n'+'历时：%s'+'\n'+'无座：%s 票价：%s'+'\n'+'硬座：%s 票价：%s'+'\n'+'硬卧：%s 票价：%s'+\
                    '\n'+'软卧：%s 票价：%s'+'\n'+'商务座：%s 票价：%s'+'\n'+'一等座：%s 票价：%s'+'\n'+'二等座：%s 票价：%s'+'\n') % \
                      (item['train_name'],rdic(item['from_station']),rdic(item['to_station']),\
                       item['time_from'],item['time_to'],item['time_lasts'],\
                       item['no_seat'],price['WZ'] if 'A3' in price else '' ,\
                       item['hard_seat'],price['WZ'] if 'A3' in price else '',\
                       item['hard_sleeper'],price['A3'] if 'A3' in price else '',\
                       item['soft_sleeper'],price['A4'] if 'A4' in price else '',\
                       item['business_seat'],price['A9'] if 'A9' in price else '',\
                       item['first_seat'],price['M'] if 'M' in price else '',\
                       item['second_seat'],price['WZ'] if 'M' in price else ''))
            else:
                print(item['status'])

if __name__ == "__main__":
    main()
    

