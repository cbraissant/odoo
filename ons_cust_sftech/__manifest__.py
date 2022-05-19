# -*- coding: utf-8 -*-
# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "SF Tech Cust: V14",
    "summary": "Open Net Customization for SF Tech",
    "description": "Open Net Customization for SF Tech - V14",
    "category": "Open Net customizations",
    "author": "Open Net Sàrl",
    "depends": [
        "sale_management",
        "mrp",
    ],
    "version": "14.0",
    "auto_install": False,
    "website": "https://www.open-net.ch",
    "license": "AGPL-3",
    "data": [
        "views/actions.xml",
        "views/view_body_part.xml",
        "views/view_measures.xml",
        "views/view_measures_line.xml",
        "views/view_mrp_bom.xml",
        "views/view_mrp_production.xml",
        "views/view_partners.xml",
        "views/view_product.xml",
        "views/view_sale_order.xml",
        "views/view_sale_order_template.xml",
        "views/report_invoice_document.xml",
        "views/report_saleorder_document.xml",
        "views/report_mrporder.xml",
        "views/report_web_internal_layout.xml",
        "data/ons_measure_type.xml",
        "data/product_product.xml",
        "security/ir_model_access.xml",
    ],
    "installable": True,
}
