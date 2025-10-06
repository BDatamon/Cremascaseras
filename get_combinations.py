import config
import requests


def get_combination(id):
    try:
        url = f"{config.prestashop_url}/combinations/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('combination')
            print(f"🎉🎉 Combinacion obtenida: {id}")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del combination {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_combination: {e}')
        return None



def get_producto_id_ps_odoo(ps_id):
    try:
        domain = [[('x_studio_p_id', '=', ps_id)]]
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.template',
            'search_read',
            domain,
            {'fields':['x_studio_p_id']}
        )
        if result:
            return int(result[0]['x_studio_p_id'])
        else:
            print('🔍 producto no encontrado en Odoo')
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({ps_id}): {e}")
        return None   
