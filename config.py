import requests
import xmlrpc.client

#Conexion PrestaShop
base_url =       "https://www.cremas-caseras.es"
api_key =        "KE9GISWX42MGE4PV9UZLQP4WSFHW3H2P"                  
prestashop_url = "https://www.cremas-caseras.es/api"               #"https://datamon2.ginernet.net/api"

print('☁️Conectandome...')

response = requests.get(prestashop_url, auth=(api_key, ''))

if response.status_code == 200:
    print('✅Conexion exitosa PrestaShop')
else:
    print('❌Conexion defectuosa:', response.status_code, response.text)



#Conexion Odoo
url = "https://cremas-caseras.odoo.com"
db = "cremas-caseras"
username = "bocampo@datamon.es"
password = "f8c8ee78499c071364dbec8dcdcdb8f9c402b98d"

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"✅ Conexión a Odoo exitosa. Usuario ID: {uid}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

