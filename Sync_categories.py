import config
import requests
import json
import base64

def get_categories_id(): 
    try:
        url = f"{config.prestashop_url}/categories?output_format=JSON&filter[active]=1"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            category_list = data.get('categories', [])
            print(f"🎉🎉 Se obtuvieron: {len(category_list )} categorias activas")
            return category_list
        else:
            print(f"❌❌Error al obtener categorias {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_categories: {e}')
        return None
    

def get_categories_details(id):
    try:
        url = f"{config.prestashop_url}/categories/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('category', {})
            print(f"🎉🎉 Detalles de la categoria obtenidos , Id del producto: {id}")
            return data
        else:
            print(f"❌❌Error al obtener Detalles de categoria {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en obtener categorias: {e}')
        return None    


def create_categories(name, id):
    try:
        datos = { 'x_studio_p_id': id, 'name': name }
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.category',
            'create',
            [datos]
        )
        if result:
            print(f"🥏🥏  categoria creada: (nombre:{name}) (ID: {id})")
            return result
        else:
            print(f"❌❌Error al crear categoria: {name}")
            return None        
    except Exception as e:
        print(f"❌ Error obteniendo value_id_odoo ({id}): {e}")
        return None



    #______________________________________________________________________________________________________________________

if __name__=="__main__":
    categorias_id = get_categories_id()
    if categorias_id:
        print(f'✅se obtuvieron categorias {len(categorias_id)}')
        for cat in categorias_id:
            cat_id = cat.get('id')
            detalles_categorias = get_categories_details(cat_id)
            nombre_categoria = detalles_categorias.get('name')[0]['value']
            id_categoria = detalles_categorias.get('id')
            crear_categorias_odoo = create_categories(nombre_categoria, id_categoria)
        

