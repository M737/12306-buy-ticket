import requests
import warnings
import json
import urllib.request
from PIL import Image
import time
import re
warnings.filterwarnings("ignore")

class Login:
    def __init__(self):
        self.headers = {'Origin':'https://kyfw.12306.cn',
                        'Referer':'https://kyfw.12306.cn/otn/login/init',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3192.0 Safari/537.36'
                       }
        self.session = requests.Session()
        
    def get_captcha(self):
        captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
        cap_res = self.session.get(url=captcha_url, headers=self.headers, verify=False)
        captcha_name = 'captcha.gif'
        with open(captcha_name,'wb') as f:
            f.write(cap_res.content)
            time.sleep(1)
        im = Image.open('captcha.gif')
        im.show()
        time.sleep(5)
        im.close()
        
    def captcha_check(self):
        dic = {'1':'35,35','2':'105,35','3':'175,35','4':'245,35','5':'35,105','6':'105,105','7':'175,105','8':'245,105'}
        num = input('请输入正确图片的序号：')
        valuelist = []
        lis = num.split('.')
        for i in lis:
            value = dic[i]
            valuelist.append(value)
        answer = ','.join(valuelist)
        cap_check_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        cap_data = {'login_site':'E',
                    'rand':'sjrand',
                    'answer':answer}
        captcha_res = self.session.post(url=cap_check_url, data=cap_data, headers=self.headers, verify=False)
        
        print(captcha_res.json()['result_message'])
        return captcha_res.json()['result_code']

    def login_in(self,username, password):
        login_url = 'https://kyfw.12306.cn/passport/web/login'
        form_data = {'username':username,
                    'password':password,
                    'appid':'otn'}
        res = self.session.post(url=login_url, data=form_data, headers=self.headers, verify=False)
        #print(res.text)
        print(res.json()["result_message"])
        return res.json()["result_code"]

    def get_uamtk(self):
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        data = {'appid':'otn'}
        res = self.session.post(url,data=data,headers=self.headers)
        return res.json()["result_code"],res.json()["newapptk"]        

    def get_uamauthclient(self,tk):
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        data = {'tk': tk}
        res = self.session.post(url,data=data,headers=self.headers)
        return res.json()["result_code"]
    
    def get_info(self):
        info_url = 'https://ad.12306.cn/sdk/webservice/rest/appService/getAdAppInfo.json'
        data = {'placementNo':'0004',
                'clientType':'2',
                'billMaterialsId':'94fab329fdb34059bd42aaf8501a80c0'}
        res = self.session.get(url=info_url,headers=self.headers,params=data)
        return res.json()['code']

    def get_left_ticket(self, date):
        leftTicket_url = 'https://kyfw.12306.cn/otn/leftTicket/query'
        data = {'leftTicketDTO.train_date':date,
                'leftTicketDTO.from_station':'XAY',
                'leftTicketDTO.to_station':'WHN',
                'purpose_codes':'ADULT'}
        res = self.session.get(url=leftTicket_url,headers=self.headers,params=data)
        if res.status_code == 200:
            datas = res.json()['data']['result']
            data = datas[1].split('|')
            secretStr = data[0]
            leftTicket = data[12]
            secretStr = str(secretStr).replace(r'%2F','/').replace('%0A','\n').replace('%2B','+')
            return res.json()['status'],secretStr,leftTicket

    def check_user(self):
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        data = {'_json_att':''}
        res = self.session.post(url,data=data,headers=self.headers)
        return res.json()['status'] 

    def submit_order(self,secretStr, date):
        order_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {'secretStr':secretStr,
                'train_date':date,
                'back_train_date':time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'tour_flag':'dc',
                'purpose_codes':'ADULT',
                'query_from_station_name':'西安',
                'query_to_station_name':'武汉',
                'undefined':''}
        res = self.session.post(url=order_url, data=data, headers=self.headers)
        print(secretStr,)
        print('-------------------')
        print(res.json())
        return res.json()['status'] 

    def get_initDC(self):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = {'_json_att':''}
        res = self.session.post(url, data=data, headers=self.headers)
        token = re.search("var globalRepeatSubmitToken = '(.*?)';", res.text)
        token = token.group(1)
        key_check_isChange=re.search("'key_check_isChange':'(.*?)'", res.text).group(1)
        return token, key_check_isChange

    def get_dtos(self,token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {'_json_att':'',
                'REPEAT_SUBMIT_TOKEN':token}
        res = self.session.post(url,data=data,headers=self.headers)
        #print(res.text)
        return res.json()['status'] 

    def check_order(self,token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = {'cancel_flag':'2',
                'bed_level_order_num':'000000000000000000000000000000',
                'passengerTicketStr':'3,0,1,{},1,{},{},N'.format(name, self_id, phone_num),  # 名字，身份证号码，手机号码
                'oldPassengerStr':'{},1,{},1_'.format(name, self_id), #名字，身份证号码
                'tour_flag':'dc',
                'randCode':'',
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN':token}
        res = self.session.post(url, data=data, headers=self.headers)
        return res.json()['status']

    def get_queue(self,leftTicket,token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        data = {'train_date':'Thu Nov 09 2017 00:00:00 GMT+0800 (中国标准时间)',
                'train_no':'850000K86282',
                'stationTrainCode':'K862',
                'seatType':'3',
                'fromStationTelecode':'XAY',
                'toStationTelecode':'HKN',
                'leftTicket':leftTicket,
                'purpose_codes':'00',
                'train_location':'J1',
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN':token}
        res = self.session.post(url, data=data, headers=self.headers)
        print(res.text)
        return res.json()['status']

    def confirm_queue(self, token, leftTicket, key_check_isChange):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {'passengerTicketStr':'3,0,1,{},1,{},{},N'.format(name, self_id, phone_num),  # 名字，身份证号码，手机号码
                'oldPassengerStr':'{},1,{},1_'.format(name, self_id), #名字，身份证号码
                'randCode':'',
                'purpose_codes':'00',
                'key_check_isChange':key_check_isChange,
                'leftTicketStr':leftTicket,
                'train_location':'J1',
                'choose_seats':'',
                'seatDetailType':'000',
                'roomType':'00',
                'dwAll':'N',
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN':token
                }
        res = self.session.post(url, data=data, headers=self.headers)
        print(res.text)
        return res.json()['status']
    def query_order(self, token):
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?'
        data = {'random':time.time()*1000,
                'tourFlag':'dc',
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN':token}
        res = self.session.get(url,params=data, headers=self.headers)
        print(res.text)


def main():
    login = Login()
    check = False
    while not check:
        login.get_captcha()
        check_code = login.captcha_check()
        if check_code == str(4):
            break
    username = input('请输入登录用户名：')
    password = input('请输入登录密码：')
    login_code = login.login_in(username, password)
    if login_code != 0:
        print("登录失败")
        return
    code,tk = login.get_uamtk()
    time.sleep(1)
    if code != 0:
        print("获取uamtk失败")
        return
    if login.get_uamauthclient(tk) != 0:
        print("获取uamauthclient失败")
        return
    if login.get_info() != '00':
        print("获取信息失败")

    date = input("请输入购票时间，格式如：2018-01-01：")
    status, secretStr,leftTicket = login.get_left_ticket(date)
    if not status:
        print("获取余票信息失败")
        return
    if not login.check_user():
        print("验证用户失败")
        return
    if not login.submit_order(secretStr, date):
        print("提交用户失败")
        return
    token, key_check_isChange = login.get_initDC()
    if not login.get_dtos(token):
        return    
    if not login.check_order(token):
        return
    if not login.get_queue(leftTicket,token):
        return
    login.confirm_queue(token,leftTicket,key_check_isChange)
    login.query_order(token)
    print("购票成功，请前往12306支付")



if __name__ == '__main__':
    main()
    

    
