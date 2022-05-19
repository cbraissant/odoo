from tqdm import tqdm
import html
import json
import logging
import re
import requests
import sys
import xmlrpc.client

logging.basicConfig(filename='log.txt', encoding='utf-8', level=logging.ERROR)
clean_html = re.compile('<.*?>')

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
orders = []

while True:
    response = requests.request(
        'GET',
        '{}/2.0/kb_invoice?limit=2000&offset={}'.format(bexio_url, offset),
        headers=headers
    )
    new_orders = json.loads(response.text)

    if len(new_orders) == 0:
        break

    orders.extend(new_orders)
    offset += 2000

bexio_res_partner_id = models.execute_kw(
    db, uid, password, 'res.partner', 'search_read', [[['name', '=', 'Bexio']]], {
        'fields': ['id'],
        'limit': 1
    }
)[0]['id']
bexio_product_product_id = models.execute_kw(
    db, uid, password, 'product.product', 'search_read', [[['name', '=', 'Bexio']]], {
        'fields': ['id'],
        'limit': 1
    }
)[0]['id']
default_tax_id = models.execute_kw(
    db, uid, password, 'account.tax', 'search_read',
    [[['description', '=', '7.7% Incl.']]], {
        'fields': ['id'],
        'limit': 1
    }
)[0]['id']

for order in tqdm(orders):
    try:
        response = requests.request(
            'GET',
            '{}/2.0/kb_invoice/{}'.format(bexio_url, order['id']),
            headers=headers
        )
        order_details = json.loads(response.text)

        contact_id = models.execute_kw(
            db, uid, password, 'res.partner', 'search_read',
            [[['ons_bexio_id', '=', order['contact_id']]]], {
                'fields': ['id'],
                'limit': 1
            }
        )
        if len(contact_id) == 0:
            contact_id = bexio_res_partner_id
        else:
            contact_id = contact_id[0]['id']

        existing_so = models.execute_kw(
            db, uid, password, 'sale.order', 'search_read',
            [[['ons_bexio_id', '=', order_details['id']]]], {
                'fields': ['id'],
                'limit': 1
            }
        )
        sale_order = {
            'ons_bexio_name': order_details['document_nr'],
            'ons_bexio_title': order_details['title'],
            'ons_bexio_date': order_details['is_valid_from'],
            'ons_bexio_id': order_details['id'],
            'partner_id': contact_id,
            'state': 'done',
        }
        if existing_so:
            sale_order_id = existing_so[0]['id']
            models.execute_kw(
                db, uid, password, 'sale.order', 'write', [[sale_order_id], sale_order]
            )
        else:
            sale_order_id = models.execute_kw(
                db, uid, password, 'sale.order', 'create', [sale_order]
            )

            for position in order_details['positions']:
                sale_order_line = {
                    'name':
                        html.unescape(
                            re.sub(
                                clean_html, '', position['text'].replace('<br />', '\n')
                            )
                        ),
                    'order_id': sale_order_id,
                }
                if position['type'] in [
                    'KbPositionArticle', 'KbPositionCustom', 'KbPositionDiscount'
                ]:
                    product_id = bexio_product_product_id
                    if position['type'] == 'KbPositionArticle':
                        product_product_id = models.execute_kw(
                            db, uid, password, 'product.product', 'search_read',
                            [[['ons_bexio_id', '=', position['article_id']]]], {
                                'fields': ['id'],
                                'limit': 1
                            }
                        )
                        if len(product_product_id):
                            product_id = product_product_id[0]['id']
                    sale_order_line['product_id'] = product_id
                    if position['discount_in_percent']:
                        sale_order_line['discount'] = position['discount_in_percent']
                    if position['type'] == 'KbPositionDiscount':
                        sale_order_line['product_uom_qty'] = 1
                        sale_order_line['qty_delivered'] = 1
                        sale_order_line['price_unit'] = '-' + position['discount_total']
                        sale_order_line['tax_id'] = [default_tax_id]
                    else:
                        sale_order_line['product_uom_qty'] = position['amount']
                        sale_order_line['qty_delivered'] = position['amount']
                        sale_order_line['price_unit'] = position['unit_price']
                        sale_order_line['tax_id'] = [default_tax_id]
                elif position['type'] == 'KbPositionText':
                    sale_order_line['display_type'] = 'line_section'
                else:
                    raise Exception('Unknow position type')
                    continue
                models.execute_kw(
                    db, uid, password, 'sale.order.line', 'create', [sale_order_line]
                )
    except KeyboardInterrupt:
        sys.exit()
    except Exception as err:
        logging.error('Error on {}/2.0/kb_invoice/{}'.format(bexio_url, order['id']))
        logging.error(err)
