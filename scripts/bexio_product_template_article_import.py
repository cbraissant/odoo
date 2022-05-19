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
articles = []

while True:
    response = requests.request(
        'GET',
        '{}/2.0/article?limit=2000&offset={}'.format(bexio_url, offset),
        headers=headers
    )
    new_articles = json.loads(response.text)

    if len(new_articles) == 0:
        break

    articles.extend(new_articles)
    offset += 2000

for article in tqdm(articles):
    try:
        description_array = article['intern_description'].split('<br />')
        existing_product = models.execute_kw(
            db, uid, password, 'product.template', 'search_read',
            [[['ons_bexio_id', '=', article['id']]]], {
                'fields': ['id'],
                'limit': 1
            }
        )
        content = {
            'ons_bexio_id': article['id'],
            'name': description_array[0],
            'default_code': article['intern_code'],
            'lst_price': article['sale_price'],
        }
        if existing_product:
            id = existing_product[0]['id']
            models.execute_kw(
                db, uid, password, 'product.template', 'write', [[id], content],
                {'context': {
                    'lang': 'fr_FR'
                }}
            )
        else:
            id = models.execute_kw(
                db, uid, password, 'product.template', 'create', [content],
                {'context': {
                    'lang': 'fr_FR'
                }}
            )

        models.execute_kw(
            db, uid, password, 'product.template', 'write', [[id], {
                'name': description_array[1]
            }], {'context': {
                'lang': 'en_US'
            }}
        )
        models.execute_kw(
            db, uid, password, 'product.template', 'write', [[id], {
                'name': description_array[2]
            }], {'context': {
                'lang': 'de_CH'
            }}
        )
    except KeyboardInterrupt:
        sys.exit()
    except Exception as err:
        logging.error('Error on {}/2.0/article/{}'.format(bexio_url, article['id']))
        logging.error(err)
