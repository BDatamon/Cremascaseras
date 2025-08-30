import requests



api_key = "F62Y8AR886NH9S2XL5VK6CLCYSQQQI34"
prestashop_url ="https://datamon2.ginernet.net/api"

print('☁️Conectandome...')

response = requests.get(prestashop_url, auth=(api_key, ''))

if response.status_code == 200:
    print('✅Conexion exitosa PrestaShop')
else:
    print('❌Conexion defectuosa:', response.status_code, response.text)


