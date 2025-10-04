import config
import requests


def get_combination(id):
    try:
        url = f"{config.prestashop_url}/combinations/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('combination')
            print(f"🎉🎉 Combinacion obtenida")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del combination {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_combination: {e}')
        return None


    
