import pyinotify
import os
import setproctitle
import json
import smtplib
import requests
import IPy
from email.mime.text import MIMEText
setproctitle.setproctitle("MyDenyUfw")
_user = "1121508831@qq.com"
_pwd = "bxsbjkfpcgxugdcg"
_to  = "1121508831@qq.com"
qq_email = smtplib.SMTP_SSL("smtp.qq.com", 465)
qq_email.login(_user, _pwd)
MAX_FAIL = 4

ip_dic = json.load(open('/root/lastb.log','r'))
print(ip_dic)

def get_location(ip):
    url =  'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?co=&resource_id=6006&t=1529895387942&ie=utf8&oe=gbk&cb=op_aladdin_callback&format=json&tn=baidu&cb=jQuery110203920624944751099_1529894588086&_=1529894588088&query=%s'%ip
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    html = r.text
    c1 = html.split('location":"')[1]
    c2 = c1.split('","')[0]
    return c2
def check_ip(ip):
    try:
        IPy.IP(ip)
        return True
    except Exception as e:
        print(e)
        return False


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        size = os.path.getsize('/var/log/btmp')
        print(size)
        if size != 0:
            read_str = os.popen("lastb |awk '{print $3}'|uniq -c|awk '{print $2\"=\"$1;}'").read()
            ip_list = read_str.split('\n')
            ip_list.pop()
            ip_list.pop()
            ip_list.pop()
            # print(ip_list)
            for ip_tmp in ip_list:
                ip = ip_tmp.split('=')
                # print(ip)
                if ip_dic.get(ip[0]) :
                    ip_dic[ip[0]] = ip_dic[ip[0]] + int(ip[1])
                else:
                    ip_dic[ip[0]] = int(ip[1])
                if ip_dic[ip[0]] > MAX_FAIL:
                    tmp_fail_time = ip_dic[ip[0]]
                    del [ip_dic[ip[0]]]
                    with open("/etc/hosts.deny",mode="a") as data:
                        out = "ALL: " + ip[0][0:ip[0].rfind('.')] + '.*' + '\n'
                        data.write(out)
                    data.close()
                    try:
                        ip_loc = []
                        if check_ip(ip[0]):
                            ip_loc = get_location(ip[0])
                        msg_box = ip[0] + "尝试登录了" + str(tmp_fail_time) + "次" +"\n" + ip[0][0:ip[0].rfind('.')] + '.*' + "已加入内名单\n" + "IP地址位置 : " + ' '.join(ip_loc)
                        print(msg_box)
                        msg = MIMEText(msg_box)
                        msg["Subject"] = "hik服务器提醒"
                        msg["From"] = _user
                        msg["To"] = _to
                        qq_email.sendmail(_user, _to, msg.as_string())
                        qq_email.quit()
                        print ("发送成功")
                    except (qq_email.smtplib.SMTPException, e):
                        print ("发送失败")
                os.system("echo > /var/log/btmp")
            print(ip_dic)


if __name__ == '__main__':
    monitor_loop = None
    try:
        monitor_obj = pyinotify.WatchManager()
        monitor_obj.add_watch("/var/log/btmp",pyinotify.IN_MODIFY)
        event_handler = MyEventHandler()
        monitor_loop= pyinotify.Notifier(monitor_obj, event_handler)
        monitor_loop.loop()
    finally:
        if monitor_loop:
            print("停止")
            monitor_loop.stop()
        json_str = json.dumps(ip_dic) #dumps
        with open('/root/lastb.log','w+') as f:
            f.write(json_str)
        f.close()
        print("结束")
