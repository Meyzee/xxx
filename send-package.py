import sys
import json
import requests
import threading
from PIL import Image
from Queue import Queue

# create session
requests = requests.Session()

# system settings
args = len(sys.argv) - 1

# user settings
threads = 20
amount = 0

def get_captcha():
    while True:
        print "\n[*] Requesting captcha"
        try:
            response = requests.get('https://my.axisnet.id/index.php/register/captcha/login/1')
        except:
            print "\n[!] Network Error!"
        else:
            print '[*] Showing captcha'
            path='D:\\Terminal\\python\\axis\\temp\\captcha.png'
            with open(path, "wb") as file:
                file.write(response.content)
            Image.open(path).show()
            print '[*] Done!'
            return True

def signin():
    global number, password, captcha
    load_captcha = True
    while True:
        if (load_captcha == True):
            get_captcha()
            captcha = raw_input("\n[?] Captcha : ")
        else:
            load_captcha = True
        
        form = {}
        form["username"] = str(number)
        form["password"] = str(password)
        form["captcha_login"] = str(captcha)
        
        try:
            print "\n[*] Sign in"
            response = requests.post('https://my.axisnet.id/home/loginex', data=form)
        except:
            print "\n[!] Network Error!"
            load_captcha = False
        else:
            try:
                result = json.loads(response.text)
            except ValueError:
                print "\n[!] Response not valid!"
            else:
                if (result["code"] == 1):
                    print "[*] Done!\n"
                    return True 
                elif (result["code"] == "-2"):
                    print "\n[!] %s" % (result["err_msg"])
                else:
                    print "\n[!] %s" % (result["message"])
                return False

class buy_package(threading.Thread):
    def __init__(self, queue_package_id, amount):
        super(buy_package, self).__init__()

        self.package_id = queue_package_id
        self.amount     = amount
        self.daemon     = True
    
    def run(self):
        while True:
            package_id = self.package_id.get()
            amount     = self.amount
            try:
                self.send(str(package_id), str(amount))
            except Exception as e:
                print '[!] Error : %s' % (e)
            self.package_id.task_done()

    def send(self, package_id, amount):

        form = {}
        form["pkgid"]   = package_id
        form["amount"]  = amount       
        retry = 0 

        while True:
            try:
                response = requests.post('https://my.axisnet.id/home/beli_paket', data=form)
            except:
                retry += 1
            else:
                try:
                    result = json.loads(response.text)
                except ValueError:
                    retry += 1
                else:
                    if (result['status'] == '1'):
                        if (retry == 0):
                            print '[*] %s : Done!' % (package_id)
                        else:
                            print '[*] %s : Done! (%s)' % (package_id, retry)
                    elif (result['status'] == '-1'):
                        print '[!] %s : %s' % (package_id, result['Message'])
                    else:
                        print result
                    return


if (args < 3):
    print ""
    print "[*] python send-package.py (number) (password) (package)"
    print "[*]"
    print "[*] python send-package.py (number) (password) (package-start) (package-stop)"
    sys.exit()
else:
    number = sys.argv[1]
    password = sys.argv[2]
    start = sys.argv[3]
    if (args == 4):
        stop = sys.argv[4]
    else:
        stop = start

if signin():

    queue_package_id = Queue()

    for i in range(int(threads)):
        thread = buy_package(queue_package_id, amount)
        thread.start()

    for package_id in range(int(start), int(stop)+1):
        queue_package_id.put(package_id)

    queue_package_id.join()

