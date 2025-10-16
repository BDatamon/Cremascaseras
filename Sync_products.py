import config
import requests
import base64

from get_combinations import get_combination, get_producto_id_ps_odoo
from get_values_attributes import get_values, get_attributes, get_id_attribute_odoo,get_value_id_odoo,search_variant_odoo,update_variante


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
            print(f"🎉🎉 Detalles del producto obtenidos , Id del producto: {id}")
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
        if product_up:
            print(f"🥏🥏--------------------- Producto creado: {nombre} (ID: {id_product})")
            return product_up
        else:
            print('❌No se pudo crear el producto')
        return None

    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None
    


#_________________________________________________PRODUCT SYNCHRONIZATION_________________________________________________________________________________

subidos=[]


if __name__=="__main__":
    #Obtener IDs de PRODUCTOS
    productos_id = get_products_id()
    if productos_id:
        for id in productos_id:                               #1. for es para productos
            id_product = id.get('id')
            producto_detail = get_productos_details(id_product)
            if producto_detail:
                nombre = producto_detail.get('name')[0]['value']
                price_venta = producto_detail.get('price')
                coste = producto_detail.get('wholesale_price')
                description = producto_detail.get('description')[0]['value']
                referencia =producto_detail.get('reference')
                peso = producto_detail.get('weight')
                #Obtener Id de la IMAGEN que esta dentro del objeto associations
                field_image = producto_detail.get('associations', {}).get('images')
                id_image = field_image[0]['id'] if field_image else None
                imagen_producto = get_image(id_image, nombre)
            

                #Mira si tiene COMBINACIONES ese producto y las obtiene
                name_attribute = None
                name_value = None
                # Diccionario para agrupar valores por atributo
                atributos_valores = {}

                #Obtener combinaciones 
                existe_combination = producto_detail['id_default_combination']
                if existe_combination != 0:
                    print(f'🪀 El producto "{nombre}" tiene combinaciones')
                    combinations = producto_detail.get('associations').get('combinations', [])
                    for combination in combinations:              #2. for es para combinaciones                            
                        id_combination = combination.get('id')
                        obtener_combination = get_combination(id_combination)

                        #Mira si tiene VALORES y las obtiene por producto
                        product_option_values = obtener_combination.get('associations', {}).get('product_option_values', [])
                        for value in product_option_values:        #3. for es para valores
                            value_id = value.get('id')
                            obtener_value = get_values(value_id)
                            name_value = obtener_value.get('name')[0].get('value')
                            id_attribute = obtener_value.get('id_attribute_group')

                            #Obtener ARIBUTOS por cada producto
                            obtener_attributes = get_attributes(id_attribute)
                            name_attribute = obtener_attributes.get('name')[0].get('value')

                            # Agrupar valores por atributo
                            if name_attribute not in atributos_valores:
                                atributos_valores[name_attribute] = []
                            if name_value not in atributos_valores[name_attribute]:
                                atributos_valores[name_attribute].append(name_value)
                        

                #Datos Odoo
                producto_in_odoo = get_producto_id_ps_odoo(id_product)
                if producto_in_odoo != id_product:
                    producto_odoo = {
                        "name": nombre,
                        "x_studio_p_id": id_product,                
                        "default_code": referencia,
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
                    upload_odoo = create_product_odoo(producto_odoo)
                    
                    if upload_odoo:
                        subidos.append(id) #Esto es para contabilizar cuantos productos se han subido


                        
                    #AQUI VOY A GUARDAR TODOS LOS ID'S DE ODOO Y SE BUSCAN POR MEDIO DE LOS NOMBRES DE CADA NOMBRE DEL VALOR
                        for name_attribute, values_list in atributos_valores.items():
                            id_attribute_odoo = get_id_attribute_odoo(name_attribute)
                            value_ids_odoo = []

                            for v in values_list:
                                value_id_odoo = get_value_id_odoo(v)
                                if value_id_odoo:
                                    value_ids_odoo.append(value_id_odoo)

                            if id_attribute_odoo and value_ids_odoo:
                        #Verificamos si ya estan los atributos y valores puestos en el modulo 'product.template.attribute.line'
                                try:
                                    existing_line = config.models.execute_kw(
                                    config.db, 
                                    config.uid, 
                                    config.password,
                                    'product.template.attribute.line', 
                                    'search',
                                    [[
                                        ['product_tmpl_id', '=', upload_odoo],
                                        ['attribute_id', '=', id_attribute_odoo]
                                    ]],
                                    {'limit': 1}
                                )
                            #Si no exieten CREAMOS ESAS VARIANTES en el producto
                                    if not existing_line:
                                        config.models.execute_kw(
                                            config.db,
                                            config.uid,
                                            config.password,
                                            'product.template.attribute.line',
                                            'create',
                                            [{
                                                "product_tmpl_id": upload_odoo,
                                                "attribute_id": id_attribute_odoo,
                                                "value_ids": [(6, 0, value_ids_odoo)]
                                            }]
                                        )
                                        print(f"🧩 Atributo '{name_attribute}' con valores {values_list} vinculado al producto {nombre}")
                                except Exception as e:
                                    print(f"❌ Error al crear {e}")
                                    break 
                else:
                    print(f'🔍🔍 El producto {nombre} ya existe en Odoo')

##############################
# ACTUALIZAR VARIANTES
# ############################


            if existe_combination != 0:
                    combinations = producto_detail.get('associations').get('combinations', [])
                    for combination in combinations:              #2. for es para combinaciones                            
                        id_combination = combination.get('id')
                        obtener_combination = get_combination(id_combination)
                        

                        product_option_values = obtener_combination.get('associations', {}).get('product_option_values', [])
                
                        # Lista para guardar los IDs de valores en Odoo
                        valores_odoo_ids = []
                
                        for value in product_option_values:
                            value_id = value.get('id')
                            obtener_value = get_values(value_id)
                            name_value = obtener_value.get('name')[0].get('value')
                    
                            # Obtener el ID del valor en Odoo x medio del nombre
                            value_id_odoo = get_value_id_odoo(name_value)
                            if value_id_odoo:
                                valores_odoo_ids.append(value_id_odoo)
                
                        # Ahora buscamos la variante en Odoo que tenga EXACTAMENTE estos valores
                        if valores_odoo_ids: 
                            buscar_variante_odoo = search_variant_odoo(upload_odoo, valores_odoo_ids)   
                
                    
                            if buscar_variante_odoo:
                                # Preparar los datos de la combinación de PrestaShop
                                datos_variante = {
                                    'lst_price': float(obtener_combination.get('price', 0)),  # Precio
                                    'weight': float(obtener_combination.get('weight', 0)),    # Peso
                                    'barcode': obtener_combination.get('ean13', ''),          # Código de barras
                                    'x_studio_ps_id': id_combination,                          # ID de PrestaShop
                                    'default_code': obtener_combination.get('reference', '')  # Referencia
                                }
                        
                                # Actualizar la variante en Odoo
                                actualizada_variante = update_variante(buscar_variante_odoo,datos_variante,nombre, id_combination, valores_odoo_ids)
                                if actualizada_variante:
                                    print("🧩 Se actualizo la variante correctamente")

                            else:
                                print(f"⚠️ No se encontró variante en Odoo para combinación {id_combination}")
                         
print(f"🎊🎉Proceso terminado: Productos creados en Odoo {len(subidos)}")









                    
     