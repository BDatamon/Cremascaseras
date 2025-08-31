import requests
import xmlrpc.client

#Conexion PrestaShop
base_url = "https://datamon2.ginernet.net"
api_key = "F62Y8AR886NH9S2XL5VK6CLCYSQQQI34"
prestashop_url ="https://datamon2.ginernet.net/api"

print('☁️Conectandome...')

response = requests.get(prestashop_url, auth=(api_key, ''))

if response.status_code == 200:
    print('✅Conexion exitosa PrestaShop')
else:
    print('❌Conexion defectuosa:', response.status_code, response.text)



#Conexion Odoo
url = "https://cremascaseras.odoo.com"
db = "cremascaseras"
username = "bocampo@datamon.es"
password = "7cf1dfb233d14457bff392c9ad8e9fe8e517d541"

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"✅ Conexión a Odoo exitosa. Usuario ID: {uid}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

