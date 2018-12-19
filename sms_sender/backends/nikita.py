import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

from django.conf import settings
from django.utils.translation import gettext as _


def get_settings_value(attr, default_value):
    return getattr(settings, attr) if hasattr(settings, attr) else default_value


STATUS_CHOICES = {'0': _('Success'),
                  '1': _('Format error'),
                  '2': _('Username or password incorrect'),
                  '3': _('Incorrect IP address of sender'),
                  '4': _('Insufficient funds for sending all sms messages'),
                  '5': _('Not approved sender name'),
                  '6': _('Message was stopped due to stop phrases'),
                  '7': _('Invalid phone number format'),
                  '8': _('Wrong time format'),
                  '9': _('Blocked due to spam filtering'),
                  '10': _('Blocked due to repeated id'),
                  '11': _('Test message was successful, but not sent')}


class NikitaKg(object):
    def __init__(self):
        self.sender_name = get_settings_value('SMS_SENDER_NAME', '')
        self.login = get_settings_value('SMS_LOGIN', '')
        self.password = get_settings_value('SMS_PASSWORD', '')

    def send_sms(self, phones, message, time=None, sender=None):
        if not isinstance(phones, list):
            phones = [phones]
        if not sender:
            sender = self.sender_name
        sender = sender if sender else ''
        time = time if time else ''
        timestamp = str(round(datetime.datetime.now().timestamp(), 2)).replace('.', '')
        url = 'https://smspro.nikita.kg/api/message'
        headers = {'Content-Type': 'application/xml'}
        data = self.make_xml_document(phone_numbers=phones, message=message, sender=sender, time=time, id=timestamp)
        request = Request(url, headers=headers, data=data)
        response = urlopen(request).read()
        xml_response = ET.fromstring(response)
        children = xml_response.getchildren()

        result = {'phone': phones}
        for i in children:
            if i.tag.endswith('status'):
                result['status'] = STATUS_CHOICES[i.text]
            elif i.tag.endswith('id'):
                result['id'] = i.text
        return result

    def make_xml_document(self, phone_numbers, message, sender, id, time=None, test=False):
        root = ET.Element('message')
        login = ET.SubElement(root, 'login')
        login.text = self.login
        password = ET.SubElement(root, 'pwd')
        password.text = self.password
        id_element = ET.SubElement(root, 'id')
        id_element.text = id
        sender_element = ET.SubElement(root, 'sender')
        sender_element.text = sender
        text = ET.SubElement(root, 'text')
        text.text = message
        if time:
            time_element = ET.SubElement(root, 'time')
            time_element.text = time
        phones = ET.SubElement(root, 'phones')
        for number in phone_numbers:
            phone = ET.SubElement(phones, 'phone')
            phone.text = number
        if test:
            test_element = ET.SubElement(root, 'test')
            test_element.text = '1'

        xml_file = ET.tostring(root)

        return xml_file
