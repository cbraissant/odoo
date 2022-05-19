from tqdm import tqdm
import json
import logging
import requests
import sys
import xmlrpc.client

logging.basicConfig(filename='log.txt', encoding='utf-8', level=logging.ERROR)

json_file = open('config.json')
config = json.load(json_file)

bexio_url = 'https://api.bexio.com'
token = config['token']

odoo_url = config['odoo_url']
db = config['db']
username = config['username']
password = config['password']

common = xmlrpc.client.ServerProxy(
    '{}/xmlrpc/2/common'.format(odoo_url), allow_none=True
)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(
    '{}/xmlrpc/2/object'.format(odoo_url), allow_none=True
)

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(token),
}

offset = 0
contacts = []

while True:
    response = requests.request(
        'GET',
        '{}/2.0/contact?limit=2000&offset={}'.format(bexio_url, offset),
        headers=headers
    )
    new_contacts = json.loads(response.text)

    if len(new_contacts) == 0:
        break

    contacts.extend(new_contacts)
    offset += 2000

for contact in tqdm(contacts):
    try:
        existing_partner = models.execute_kw(
            db, uid, password, 'res.partner', 'search_read',
            [[['ons_bexio_id', '=', contact['id']]]], {
                'fields': ['id'],
                'limit': 1
            }
        )
        if contact['language_id'] == 1:
            lang = 'de_CH'
        elif contact['language_id'] == 2:
            lang = 'fr_FR'
        elif contact['language_id'] == 4:
            lang = 'en_US'
        else:
            lang = 'fr_FR'
        content = {
            'ons_bexio_id': contact['id'],
            'company_type': 'company' if contact['contact_type_id'] == 1 else 'person',
            'name':
                contact['name_1'] +
                (" " + contact['name_2']) if contact['name_2'] else contact['name_1'],
            'street': contact['address'],
            'zip': contact['postcode'],
            'city': contact['city'],
            'email': contact['mail'],
            'phone': contact['phone_fixed'],
            'mobile': contact['phone_mobile'],
            'website': contact['url'],
            'lang': lang
        }
        if existing_partner:
            id = existing_partner[0]['id']
            models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], content])
        else:
            models.execute_kw(db, uid, password, 'res.partner', 'create', [content])
    except KeyboardInterrupt:
        sys.exit()
    except Exception as err:
        logging.error('Error on {}/2.0/contact/{}'.format(bexio_url, contact['id']))
        logging.error(err)
