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
    


    #______________________________________________________________________________________________________________________

if __name__=="__main__":
    categorias_id = get_categories_id()
    if categorias_id:
        print(f'✅se obtuvieron categorias {len(categorias_id)}')