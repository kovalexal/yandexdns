#!/usr/bin/env python3


import sys
import json
import argparse
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request



def get_wan_ip():
    '''Gets WAN ip address from external service
    :return: IP address in a string
    '''
    return json.loads(urlopen("http://httpbin.org/ip").read().decode('utf-8'))['origin']


class YandexDNSUpdater:
    '''Class used to update Yandex DNS records
    '''
    def __init__(self, domain, token):
        '''Initializer
        :param domain: A domain to update records
        :param token: A token for Yandex DNS service (https://pddimp.yandex.ru/api2/registrar/get_token)
        :return: None
        '''

        self.domain = domain
        self.token = token

        self.url_get_records = 'https://pddimp.yandex.ru/api2/admin/dns/list?domain=' + self.domain
        self.url_edit_record = 'https://pddimp.yandex.ru/api2/admin/dns/edit'
        self.url_create_record = 'https://pddimp.yandex.ru/api2/admin/dns/add'


    def __yandexdns_get_request(self, url):
        '''Internal function, which is used to make GET request to server
        :param url: A url to make request to
        :return: A result from server
        '''

        # Create a request with custom header
        req = Request(url, headers={
            'PddToken': self.token
        })

        # Make a request and get response from server
        data = urlopen(req).read()

        # Decode response
        result = json.loads(data.decode('utf-8'))
        if result['success'] != 'ok':
            raise Exception(result['error'])

        return result


    def __yandexdns_post_request(self, url, data):
        '''Internal function, which is used to make POST request to server
        :param url: A url to make request to
        :param data: A data to post
        :return: A result from server
        '''

        # Create a request with custom header
        req = Request(url, data=str.encode(data), headers={
            'PddToken': self.token
        })

        # Make a request and get response from server
        data = urlopen(req).read()

        # Decode response
        result = json.loads(data.decode('utf-8'))
        if result['success'] != 'ok':
            raise Exception(result['error'])

        return result


    def __get_dns_records(self):
        '''Internal function, which returns all available DNS records
        :return: Records in a list (https://tech.yandex.ru/pdd/doc/reference/dns-list-docpage/)
        '''

        result = self.__yandexdns_get_request(self.url_get_records)['records']
        return result


    def _update_record(self, record, ip, ttl):
        '''Internal function, which updates available DNS record
        :param record: A record to update (https://tech.yandex.ru/pdd/doc/reference/dns-edit-docpage/)
        :param ip: An IP address to write to record
        :param ttl: DNS record time to live
        :return: Result from server
        '''

        s = 'domain={0}&record_id={1}&subdomain={2}&ttl={3}&content={4}'.format(record['domain'], record['record_id'], record['subdomain'], ttl, ip)
        return self.__yandexdns_post_request(self.url_edit_record, s)


    def _create_record(self, subdomain, ip, ttl):
        '''Internal function, which creates new DNS record
        :param subdomain: A subdomain for which a new record should be created
        :param ip: An IP address to write to record
        :param ttl: DNS record time to live
        :return: Result from server
        '''

        s = 'domain={0}&type=A&subdomain={1}&ttl={2}&content={3}'.format(self.domain, subdomain, ttl, ip)
        return self.__yandexdns_post_request(self.url_create_record, s)


    def update(self, subdomains, ip, ttl):
        '''Updates existing records or creates new records if they don`t exist
        :param subdomains: A list of subdomains to update
        :param ip: An IP address to write to record
        :param ttl: DNS record time to live
        :return: None
        '''

        # Get all available DNS records
        records = self.__get_dns_records()
        subdomains = set(subdomains)

        # Process a list of records to update
        records_to_update = [r for r in records if r['subdomain'] in subdomains and r['type'] == 'A']
        for record in records_to_update:
            self._update_record(record, ip, ttl)

        # Process a list of records to create
        create_records = subdomains - set([r['subdomain'] for r in records_to_update])
        for subdomain in create_records:
            self._create_record(subdomain, ip, ttl)


def main(argc=len(sys.argv), argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', help='Path to json configuration file', type=str)
    parser.add_argument('-i', '--ip', help='IP address', type=str)
    args = parser.parse_args()

    ip = args.ip or get_wan_ip()
    settings_file = args.settings

    with open(settings_file, 'r') as in_file:
        settings = json.loads(in_file.read())

    ttl = settings.get('ttl', None) or 600

    for domain in settings['domains']:
        updater = YandexDNSUpdater(domain['domain'], domain['PddToken'])
        updater.update(domain['subdomains'], ip, ttl)

if __name__ == '__main__':
    main()