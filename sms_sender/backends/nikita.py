import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

from django.conf import settings


def get_settings_value(attr, default_value):
    return getattr(settings, attr) if hasattr(settings, attr) else default_value


class NikitaKg(object):
    def __init__(self):
        self.sender_name = get_settings_value('NIKITA_SENDER_NAME', '')
        self.login = get_settings_value('NIKITA_LOGIN', '')
        self.password = get_settings_value('NIKITA_PASSWORD', '')

    def send_sms(self, phones, message, time=None, id=0, sender=None):
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
