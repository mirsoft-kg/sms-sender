# -*- coding: utf-8 -*-
from time import sleep
from django.utils.translation import ugettext as _
from django.conf import settings

try:
    from urllib import urlopen, quote
except ImportError:
    from urllib.request import urlopen
    from urllib.parse import quote


STATUS_CHOICES = {'0': _('Success'),
                  '1': _('Abonent does not exist'),
                  '2': _('Username or password incorrect'),
                  '3': _('On the Customer\'s account insufficient funds'),
                  '4': _('IP-address is temporarily blocked due to frequent errors in queries'),
                  '5': _('Wrong date format'),
                  '6': _('Subscriber Offline'),
                  '7': _('Invalid phone number format'),
                  '8': _('Message to phone number can not be delivered'),
                  '9': _('Sending more than one of the same request to send SMS-messages, or more than five requests for the same cost of message for a minute'),
                  '11': _('No SMS services'),
                  '13': _('Subscriber blocked'),
                  '21': _('No support for SMS'),
                  '245': _('Status is not obtained'),
                  '246': _('Time limit'),
                  '247': _('Exceed message limit'),
                  '248': _('No route'),
                  '249': _('Wrong number format'),
                  '250': _('Number not permitted settings'),
                  '251': _('Limit is exceeded on a single number'),
                  '252': _('Phone number denied'),
                  '253': _('Spam filter denied'),
                  '254': _('Baned sender id'),
                  '255': _('Declined by operator')}

STATUS_MESSAGE = {'-1': _('Waiting to send'),
                  '0': _('Passed to the operator'),
                  '1': _('Delivered'),
                  '3': _('Expired'),
                  '20': _('Unable to deliver'),
                  '22': _('Wrong number'),
                  '23': _('Denied'),
                  '24': _('Insufficient funds'),
                  '25': _('Unavailable phone number')}


def get_settings_value(attr, default_value):
    return getattr(settings, attr) if hasattr(settings, attr) else default_value


class SMSC(object):
    def __init__(self):
        self.sender_name = get_settings_value('SMS_SENDER_NAME', '')
        self.login = get_settings_value('SMSC_LOGIN', '')
        self.pasword = get_settings_value('SMSC_PASSWORD', '')
        self.smsc_post = get_settings_value('SMSC_POST', False)
        self.smsc_https = get_settings_value('SMSC_HTTPS', False)
        self.charset = get_settings_value('SMSC_CHARSET', 'utf-8')

    def send_sms(self, phones, message, translit=False, time=None, id=0, format=0, sender=None, query=None):
        formats = ["flash=1", "push=1", "hlr=1", "bin=1", "bin=2", "ping=1"]

        if not sender:
            sender = self.sender_name

        sender = quote(sender) if sender else ''
        time = time if time else ''
        args = 'cost=3&phones=%(phones)s&mes=%(mes)s&translit=%(translit)d&id=%(id)d&sender=%(sender)s&time=%(time)s' % {
            'phones': phones,
            'mes': quote(message),
            'translit': int(translit),
            'id': id,
            'sender': sender,
            'time': time
        }

        if format > 0:
            args += '&' + formats[format-1]

        if query:
            args += '&' + query

        response = self._smsc_send_cmd('send', args)

        if settings.DEBUG:
            if response[1] > "0":
                print(u"Soobschenie otpravleno uspeshno. ID: " + response[0] + u", vsego SMS: " + response[1] + u", stoimost: " + response[2] + u", balans: " + response[3])
            else:
                print(u"Oshibka #" + response[1][1:] + u", ID: " + response[0])

        result = {'id': response[0],
                  'status': STATUS_CHOICES[response[1][1:]] if response[1][1:] != '' else STATUS_CHOICES['0'],
                  'status_code': response[1][1:] if response[1][1:] != '' else '0',
                  'object': response}
        return result

    def _smsc_send_cmd(self, cmd, arg=""):
        if self.smsc_https:
            url = "https://smsc.ru/sys/" + cmd + ".php"
        else:
            url = "http://smsc.ru/sys/" + cmd + ".php"

        arg = "login=" + quote(self.login) + "&psw=" + quote(self.pasword) + "&fmt=1&charset=" + self.charset + "&" + arg

        i = 0
        ret = ""

        while ret == "" and i < 3:
            if i > 0:
                sleep(2)

            if i == 2:
                url = url.replace("://smsc.ru/", "://www2.smsc.ru/")

            try:
                if self.smsc_post or len(arg) > 2000:
                    data = urlopen(url, arg.encode(self.charset))
                else:
                    data = urlopen(url + "?" + arg)

                ret = data.read().decode('utf-8')
            except:
                ret = ""

            i += 1

        if ret == "":
            if settings.DEBUG:
                print(u"Oshibka chteniya adresa: " + url)
            ret = "," # фиктивный ответ
        return ret.split(",")
