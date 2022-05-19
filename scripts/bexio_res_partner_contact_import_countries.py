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

response = requests.request('GET', '{}/2.0/country'.format(bexio_url), headers=headers)
countries_bexio = json.loads(response.text)
countries_odoo = {}
for country_bexio in countries_bexio:
    country_odoo = models.execute_kw(
        db, uid, password, 'res.country', 'search_read',
        [[['code', '=', country_bexio['iso_3166_alpha2']]]], {
            'fields': ['id'],
            'limit': 1
        }
    )
    if len(country_odoo):
        countries_odoo[country_bexio['id']] = country_odoo[0]['id']

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
        content = {
            'country_id': countries_odoo[contact['country_id']],
        }
        if existing_partner:
            id = existing_partner[0]['id']
            models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], content])
    except KeyboardInterrupt:
        sys.exit()
    except Exception as err:
        logging.error('Error on {}/2.0/contact/{}'.format(bexio_url, contact['id']))
        logging.error(err)
