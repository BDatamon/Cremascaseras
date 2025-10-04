import config
import requests


def get_values(id):
    try:
        url = f"{config.prestashop_url}/product_option_values/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product_option_value')
            print(f"🎉🎉 value obtenido")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del product_option_value {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_values: {e}')
        return None
    


def get_attributes(id):
    try:
        url = f"{config.prestashop_url}/product_options/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product_option')
            print(f"🎉🎉 attributo obtenido")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del attribute {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_attribute: {e}')
        return None
    


def create_attribute_odoo(name, id):
    try:
        product_up = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.attribute', 
                'create',
                [{'name': name, 'x_studio_p_id': id }]
        )
        print(f"✅ attribute creado: (nombre:{name}) (ID: {id})")
        return product_up
    
    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None




def create_value_odoo(id_attribute, name_value , id_value, ):

    try:
        product_up = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.attribute.value', 
                'create',
                [{'name': name_value, 'attribute_id': id_attribute, 'x_studio_p_id': id_value }]
        )
        print(f"✅ valor creado: (nombre:{name_value}) (ID atributo: {id_attribute})")
        return product_up
    

    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None