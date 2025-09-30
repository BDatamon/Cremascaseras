import config
import requests
import json
import base64

def get_products_id(): 
    try:
        url = f"{config.prestashop_url}/products?output_format=JSON&filter[active]=1"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            products_list = data.get('products', [])
            print(f"🎉🎉 Se obtuvieron: {len(products_list )} productos activos")
            return products_list
        else:
            print(f"❌❌Error al obtener productos {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_products: {e}')
        return None



def get_productos_details(id):
    try:
        url = f"{config.prestashop_url}/products/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product')
            print(f"🎉🎉 Detalles obtenidos")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del producto {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_products: {e}')
        return None




def get_image(id_img, name):
    try: 
        base_url = config.base_url  # Usar el dominio PrestaShop real

        # Construir ruta con dígitos del id_img
        id_str = str(id_img)            #Convierte todo formato a string
        id_path = "/".join(list(id_str))#list():sirve para convertir cualquier objeto iterable (como una cadena, tupla o conjunto) en una lista
                                        #join():sirve para unir los elementos de un iterable (como una lista o tupla) en una sola cadena de texto
        url_img = f"{base_url}/img/p/{id_path}/{id_str}-home_default.jpg"
        headers = {"User-Agent": "Mozilla/5.0"} #Es un disfraz para decirle al servidor que somos un navegador web para descargar la imagen

        response = requests.get(url_img, headers=headers, timeout=10)
        response.raise_for_status()

        imagen_objeto = base64.b64encode(response.content).decode('utf-8')
        if imagen_objeto:
            print(f'✅🎉 Imagen de {name} descargada con éxito desde {url_img}')
            return imagen_objeto

    except Exception as e:
        print(f"❌ Error al descargar imagen {id_img} de {name}: {e}")
        return None




def create_product_odoo(producto_odoo):
    try:
        product_up = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.template', 
                'create',
                [producto_odoo]
        )
        print(f"✅ Producto creado: {nombre} (ID: {id_product})")
        return product_up
    

    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None
    


#_________________________________________________PRODUCT SYNCHRONIZATION_________________________________________________________________________________

subidos=[]

if __name__=="__main__":
    productos_id = get_products_id()
    if productos_id:
        for id in productos_id:
            id_product = id.get('id')
            producto_detail = get_productos_details(id_product)
            if producto_detail:
                nombre = producto_detail.get('name')[0]['value']
                price_venta = producto_detail.get('price')
                coste = producto_detail.get('wholesale_price')
                description = producto_detail.get('description')[0]['value']
                referencia =producto_detail.get('reference')
                #Obtener Id de la imagen que esta dentro del objeto associations
                field_image = producto_detail.get('associations', {}).get('images')
                id_image = field_image[0]['id'] if field_image else None
                imagen_producto = get_image(id_image, nombre)

                #Datos Odoo
                producto_odoo = {
                    "name": nombre,
                    "x_studio_p_id": referencia,
                    "list_price": price_venta,
                    "standard_price": coste,
                    "type": "consu",
                    "purchase_ok": True,
                    "sale_ok": True,
                    "uom_id": 1,  # Unidad de medida por defecto (1 = Units)
                    "currency_id": 125,  # EUR (según el ejemplo)
                    "public_description": str(description),
                    "available_in_pos": True
                }
                if imagen_producto:
                        producto_odoo["image_1920"] = imagen_producto
                #crear_productos       
                upload_odoo = create_product_odoo(producto_odoo, subidos)
                if upload_odoo:
                    subidos.append(id)

                # print(json.dumps(producto_detail, indent=2, ensure_ascii=False))    
        print(f"🎊🎉Proceso terminado: Productos creados en Odoo {len(subidos)}")