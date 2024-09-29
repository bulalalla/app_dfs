import sys
# sys.path.append("C:/Users/HUAWEI/.conda/envs/app_test/Lib/site-packages")
# mitmdump -p 18080 --mode upstream:127.0.0.1:7890 -s C:\Users\HUAWEI\Desktop\middle_process.py
import datetime
import mitmproxy.dns
import mitmproxy.http
import mitmproxy.tls
import mysql.connector
import mitmproxy

class Events:

    dns_sql = ("INSERT INTO app_domain_dns "
               "(package_name, method, protocol, qrcode, question, response, domains, add_time)"
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    https_sql = ("INSERT INTO app_domain_https "
                 "(package_name, method, protocol, qrvalue, host, uri_path, content_type, data, add_time)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    tls_sni_sql = ("INSERT INTO app_domain_tls_sni "
                   "(package_name, method, protocol, sni, add_time)"
                   "VALUES (%s, %s, %s, %s, %s)")

    def __init__(self):
        self.cnx = mysql.connector.connect(user='root',
                                           password='1234',
                                           host='localhost',
                                           port=3306,
                                           database='app_doe')
        self.packet_name = self.get_current_app()

    def get_current_app(self):
        with open('E:\\work\\app_auto_test\\mitmproxy\\currapp.txt', 'r', encoding='utf-8') as file:
            return str(file.read())
        # self.packet_name = "ins_nothing_register2"

    def dns_request(self, flow: mitmproxy.dns.DNSFlow):
        print("DNS流量")
        if flow.request:
            self.get_current_app()
            cursor = self.cnx.cursor()
            questions = flow.request.questions
            domains = list()
            questions_str = list()
            for question in questions:
                domains.append(question.name)
                questions_str.append((question.name, question.class_, question.type))
            data = (self.packet_name, 'MITM', 'DNS', 0, str(questions_str), '', str(domains), datetime.datetime.now())
            cursor.execute(self.dns_sql, data)
            cursor.close()
            self.cnx.commit()

    def dns_response(self, flow: mitmproxy.dns.DNSFlow):
        if flow.response:
            self.get_current_app()
            cursor = self.cnx.cursor()
            answers = flow.response.answers
            domains = list()
            answers_str = list()
            for answer in answers:
                domains.append(answer.name)
                answers_str.append((answer.name, answer.class_, answer.type, answer.data))
            data = (self.packet_name, 'MITM', 'DNS', '0', '', str(answers_str), str(domains), datetime.datetime.now())
            cursor.execute(self.dns_sql, data)
            cursor.close()
            self.cnx.commit()

    def requestheaders(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request:
            self.get_current_app()
            cursor = self.cnx.cursor()
            # 访问请求的信息
            req = flow.request
            if req.data.content:
                data = req.data.content.decode(encoding='utf-8')
            else:
                data = ''
            # 打印请求的主机、URI、内容类型、HTTP版本以及内容
            data = (self.packet_name, 'MITM', 'HTTPS', str(req.method).upper(), req.host, req.path,
                    req.headers.get('content-type', 'NULL'), data, datetime.datetime.now())
            cursor.execute(self.https_sql, data)
            cursor.close()
            self.cnx.commit()

    def tls_clienthello(self, data: mitmproxy.tls.ClientHelloData):
        if data.client_hello:
            self.get_current_app()
            client_hello = data.client_hello
            sni = client_hello.sni
            if sni:
                cursor = self.cnx.cursor()
                data = (self.packet_name, 'MITM', 'TLS_SNI', sni, datetime.datetime.now())
                cursor.execute(self.tls_sni_sql, data)
                cursor.close()
                self.cnx.commit()

    def done(self):
        self.cnx.close()


addons = [Events()]
