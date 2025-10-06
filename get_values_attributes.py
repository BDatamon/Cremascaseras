import config
import requests


def get_values(id):
    try:
        url = f"{config.prestashop_url}/product_option_values/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product_option_value')
            print(f"🎉🎉 value obtenido: {id}")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del product_option_value {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_values: {e}')
        return None
    

#Funcion para otener los atributos
def get_attributes(id):
    try:
        url = f"{config.prestashop_url}/product_options/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product_option')
            print(f"🎉🎉 attributo obtenido: {id}")
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
        if product_up:
            print(f"✅ attribute creado: (nombre:{name}) (ID: {id})")
            return product_up
        else:
            print(f"❌❌Error al crear attribute: {name}")
            return None   
    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None



#funcion ra acrear valores en Odoo
def create_value_odoo(id_attribute, name_value, value_id  ):
    try:
        datos = {'name': name_value, 'attribute_id': id_attribute, 'x_studio_p_id': value_id}
        product_up = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.attribute.value', 
                'create',
                [datos]
        )
        if product_up:
            print(f"✅ valor creado: (nombre:{name_value}) (ID atributo: {id_attribute})")
            return product_up
        else:
            print(f"❌❌Error al crear valor: {name_value}")
            return None   
    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None
    


#funcion para ver si el Id de prestashop del atributo ya esta en Odoo
def get_p_id_odoo(id):
    try:
        resultado = config.models.execute_kw(
        config.db, 
        config.uid, 
        config.password,
        'product.attribute',
        'search_read',
        [[('x_studio_p_id', '=', id)]],
        {'fields': ['x_studio_p_id'], 'limit': 1}
        )
        if resultado:
            print(f"✅ Id obtenido: {resultado}")
            return resultado[0]['x_studio_p_id']
        else:
            print('❌El id del atributo ps no esta en Odoo')
            return None
    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None



#Esta funcion es para obtener el ID del atributo de Odoo por medio del nombre del atributo   
def get_id_attribute_odoo(name):
    try:
        resultado = config.models.execute_kw(
        config.db, 
        config.uid, 
        config.password,
        'product.attribute',
        'search',
        [[('name', '=', name)]],
        {'limit': 1}
        )
        if resultado:
            print(f"✅ Id obtenido: {resultado}")
            return resultado[0]
        else:
            print('❌ No se puedo obtener el Id del atributo')
            return resultado[0]
    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None



#funcion para obtener el id odoo de cada valor por medio del nombre del valor
def get_value_id_odoo(name_value):
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.attribute.value',
            'search_read',
            [[['name', '=', name_value]]],
            {'fields': ['id'], 'limit': 1}
        )
        return result[0]['id'] if result else None
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({name_value}): {e}")
        return None



#funcion para buscar el Id prestashop del valor en Odoo    
def get_value_id_ps_odoo(ps_id):
    try:
        domain = [[('x_studio_p_id', '=', ps_id)]]
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.attribute.value',
            'search_read',
            domain,
            {'fields':['x_studio_p_id']}
        )
        return result[0]['x_studio_p_id']
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({ps_id}): {e}")
        return None



#Funcion para Obtener las variantes en Odoo del product.product
def get_variantes_odoo(product_template_odoo):
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.product',
            'search_read',
            [[['product_tmpl_id', '=', product_template_odoo]]],
            {'fields':['valid_product_template_attribute_line_ids'] }
        )
        return result
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({product_template_odoo}): {e}")
        return None


def write_variantes_odoo(v,id_v,datos):
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.product',
            'write',
            [[id_v], datos],           
        )
        return result
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({v}): {e}")
        return None