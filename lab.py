import config
import requests
import base64

from get_combinations      import get_combination, get_producto_id_ps_odoo
from sync_categories       import get_category_by_ps_id
from get_values_attributes import get_values, get_attributes, get_id_attribute_odoo,get_value_id_odoo,search_variant_odoo,update_variante,search_padre_odoo
from get_values_attributes import get_product_template_product_attribute_value,search_product_atributos_valores_odoo, update_precio_product_attribute_value

def get_products_id(): 
    try:
        url = f"{config.prestashop_url}/products?output_format=JSON"
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
        else: 
            print(f'🔍 No existe imagen para el producto {name}')
            return None
    except Exception as e:
        print(f"❌ Error al descargar imagen {id_img} de {name}: {e}")
        return None


def create_product_odoo(producto_odoo,nombre, id):
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
            print(f"🥏🥏--------------------- Producto creado: {nombre} (ID: {id})")
            return product_up
        else:
            print(f'❌_____________No se pudo crear el producto: {nombre} con ID : {id}')
            return None

    except Exception as e:
        print(f"❌ Error al crear {e}")
        return None
    

def search_product_odoo(id_product):
    try:
        product = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.template', 
                'search',
                [[('x_studio_p_id', '=', id_product)]],
        )
        if product:
            print(f"🥏🥏--------------------- ID del producto en Odoo es:{product[0]}")
            return product[0]
        else:
            print(f'❌_____________Producto no esta en Odoo con ID : {id_product}')
            return None

    except Exception as e:
        print(f"❌ Error al buscar {e}")
        return None


def update_product(producto_odoo_id, nombre,id_product,referencia, precio_venta, obtener_id_categoria_odoo):
    try:
        datos_producto = {
                            "name": nombre,
                            "x_studio_p_id": id_product,                
                            "default_code": referencia,
                            "list_price": precio_venta,   #precio base igual al de 50ml
                            "type": "consu",
                            "purchase_ok": True,
                            "sale_ok": True,
                            "uom_id": 1,  # Unidad de medida por defecto (1 = Units)
                            "currency_id": 125,  # EUR (según el ejemplo)
                            "categ_id": obtener_id_categoria_odoo,
                            'is_storable': True
                        }
        product_update = config.models.execute_kw(
                    config.db, 
                    config.uid, 
                    config.password,
                    'product.template', 
                    'write',
                    [producto_odoo_id, datos_producto]
            )
        if product_update:
            print(f"🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃🔃 Producto Actualizado: {nombre} (ID: {producto_odoo_id})")
            return product_update
        else:
            print(f'❌_____________No se pudo Actualizar el producto: {nombre} con ID : {producto_odoo_id}')
            return None

    except Exception as e:
        print(f"❌ Error al Actualizar {e}")
        return None


def get_product_product(upload_odoo):
    try:
        product = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.product', 
                'search',
                [[('product_tmpl_id', '=', upload_odoo)]],                
        )
        if product:
            return product[0]
        else:
            return None
    except Exception as e:
        print(f"❌ Error al buscar {e}")
        return None


def update_product_product(id, id_product, peso, barcode, referencia):
    try:
        product = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.product', 
                'write',
                [[(id)],
                    {
                    'x_studio_ps_id': id_product,
                    'weight': peso,
                    'barcode': barcode, 
                    'default_code': referencia,
                }]
            )
        if product:
            return product
        else:
            return None
    except Exception as e:
        print(f"❌ Error al buscar {e}")
        return None


def make_traduction(nombre, nombre_a, upload_odoo):
    try:
        traduction = config.models.execute_kw(
                config.db, 
                config.uid, 
                config.password,
                'product.template', 
                'update_field_translations',
                [[(upload_odoo)], "name",
                    {
                    'es_ES': nombre,
                    'de_DE': nombre_a
                }]
            )
        if traduction:
            return traduction
        else:
            return None
    except Exception as e:
        print(f"❌ Error al buscar {e}")
        return None


############################
# PRODUCT SYNCHRONIZATION
############################


subidos=[]

if __name__=="__main__":
    #Obtener IDs de PRODUCTOS
    productos_id = get_products_id()
    if productos_id:
        for id in productos_id:                               #1. for es para productos
            id_product = id.get('id')
            producto_detail = get_productos_details(id_product)
            if producto_detail:
                nombre = producto_detail.get('name')[0]['value'].rstrip()
                #ALEMAN
                nombre_a = producto_detail.get('name')[1]['Value'].strip()                
                precio_venta = producto_detail.get('price')
                referencia =producto_detail.get('reference').rstrip()
                peso = producto_detail.get('weight')
                barcode = producto_detail.get('ean13')
                id_categoria_product = producto_detail.get('id_category_default')
                #Obtener Id de la IMAGEN que esta dentro del objeto associations
                field_image = producto_detail.get('associations', {}).get('images')
                imagen_default = producto_detail.get('id_default_image')
                #Si hay imagen default se guarda el ID de la imagen en id_image
                if imagen_default:
                    id_image = imagen_default
                #Y si imagen_default es falsa entonces guardamos el id del field_image
                elif field_image:
                    id_image = field_image[0].get('id')
                #Si las dos opciones de arriba son false entonces id_image es igual a none
                else:
                    id_image = None

                if id_image:
                    imagen_producto = get_image(id_image, nombre)
                else:
                    print(f"⚠️ Producto {nombre} (ID {id_product}) no tiene ninguna imagen disponible")
                    imagen_producto = None
            
                #Traer categoria de de Odoo por medio de prestashop_id
                obtener_id_categoria_odoo = get_category_by_ps_id(id_categoria_product)
                if not obtener_id_categoria_odoo:
                    print(f"⚠️ Categoría PS ID {id_categoria_product} no encontrada para '{nombre}'")
                    obtener_id_categoria_odoo = 1  # Categoría por defecto
                    print(f"   → Usando categoría por defecto")

                if id_categoria_product == 81:
                    obtener_id_categoria_odoo = 209



                #Mira si tiene COMBINACIONES ese producto y las obtiene
                name_attribute = None
                name_value = None
                id_attribute_odoo = None
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
                        "list_price": precio_venta,   #precio base igual al de 50ml
                        "type": "consu",
                        "purchase_ok": True,
                        "sale_ok": True,
                        "uom_id": 1,  # Unidad de medida por defecto (1 = Units)
                        "currency_id": 125,  # EUR (según el ejemplo) 
                        "categ_id": obtener_id_categoria_odoo,
                        'is_storable': True  
                    }
                    if imagen_producto:
                            producto_odoo["image_1920"] = imagen_producto
                    else :
                        producto_odoo["image_1920"] = False

                    list_codebar = []
                    ##############################
                    # CREAMOS PRODUCTO
                    ##############################       
                    upload_odoo = create_product_odoo(producto_odoo,nombre, id_product)
                    
                    if upload_odoo:
                        subidos.append(id) #Esto es para contabilizar cuantos productos se han subido
                        #TRADUCCION
                        traduccion = make_traduction(nombre, nombre_a, upload_odoo)

                        #AQUI VOY A GUARDAR TODOS LOS ID'S DE LOS VALORES DE ODOO Y SE BUSCAN POR MEDIO DE LOS NOMBRES DE CADA NOMBRE DEL VALOR
                        for name_attribute, values_list in atributos_valores.items():
                            id_attribute_odoo = get_id_attribute_odoo(name_attribute)
                            
                            value_ids_odoo = []
                            for v in values_list:
                                value_id_odoo = get_value_id_odoo(v)
                                if value_id_odoo:
                                    value_ids_odoo.append(value_id_odoo)

                            if id_attribute_odoo and value_ids_odoo:
                                #Verificamos si ya estan los atributos y valores puestos en el modulo 'product.template.attribute.line'
                                #Si no existen lo CREAMOS ESAS VARIANTES en el producto
                                atributos_valores_producto_odoo = search_product_atributos_valores_odoo(upload_odoo, id_attribute_odoo, value_ids_odoo, name_attribute, values_list, nombre)
                                
                        #Actualizar producto sin variante product.product
                        if existe_combination == 0:
                                obtener_id_product_product = get_product_product(upload_odoo)
                                actualizar_product_product = update_product_product(obtener_id_product_product, id_product, peso, barcode, referencia)



                        ##############################
                        # ACTUALIZAR VARIANTES 
                        ##############################
                        if existe_combination != 0:
                            combinations = producto_detail.get('associations').get('combinations', [])
                            for combination in combinations:              #2. for es para combinaciones                            
                                id_combination = combination.get('id')                        
                                datos_combination = get_combination(id_combination)
                                
                                #  Usamos el ID del producto recién creado
                                id_padre_odoo = upload_odoo

                                product_option_values = datos_combination.get('associations', {}).get('product_option_values', [])
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
                        
                                # Ahora buscamos la variante en Odoo(product.product) que tenga EXACTAMENTE estos valores
                                if valores_odoo_ids: 
                                    buscar_variante_odoo = search_variant_odoo(id_padre_odoo, valores_odoo_ids)
                                    
                                    #Buscamos el Id Odoo de la variante para luego pasarle ese valor a la plantilla product.template
                                    if id_attribute_odoo == None:
                                        id_attribute_odoo = get_id_attribute_odoo(name_attribute)

                                    #Obtenemos la plantilla (product.template) exactamente en el product.template.attribute.value por medio de su respectivo valor y nos traemos campos    
                                    plantilla_product_attribute_value = get_product_template_product_attribute_value(id_padre_odoo, id_attribute_odoo, valores_odoo_ids)
                                    #Obtenemos el id de esa unica plantilla
                                    if plantilla_product_attribute_value:
                                        id_plantilla = plantilla_product_attribute_value[0]['id']
                                        #Obtenemos en presta el precio de esa combinacion
                                        precio_combinacion = datos_combination.get('price')
                                        #Y ahora si, modificamos  
                                        modificar_precio_product_attribute_value = update_precio_product_attribute_value(id_plantilla, precio_combinacion)
                                    else:
                                        print(f"⚠️ No se encontro plantilla del producto: {nombre}")
                            
                                    if buscar_variante_odoo:
                                        datos_barcode = datos_combination.get('ean13')
                                        barcode = ''
                                        if len(str(datos_barcode)) > 1:
                                            barcode = datos_barcode
                                            list_codebar.append(barcode)
                                            if barcode in list_codebar:
                                                barcode = False
                                        else: 
                                            barcode = False

                                        # Preparar los datos de la combinación de PrestaShop
                                        datos_variante = {
                                            'weight': datos_combination.get('weight'),                        # Peso
                                            'barcode': barcode,                                               # Código de barras
                                            'x_studio_ps_id': id_combination,                                 # ID de PrestaShop
                                            'default_code': datos_combination.get('reference', '').rstrip()   # Referencia
                                        }

                                        # Actualizar la variante en Odoo
                                        actualizada_variante = update_variante(buscar_variante_odoo,datos_variante,nombre, id_combination, valores_odoo_ids)
                                        # Y actualizamos el product.template para que conserve la referencia despues de que se actualiza los atributos del producto padre
                                        config.models.execute_kw(
                                        config.db,
                                        config.uid,
                                        config.password,
                                        'product.template',
                                        'write',
                                        [[upload_odoo], {'default_code': referencia}]
                                        )            
                                        if actualizada_variante:
                                            print("🔃🔃 Se actualizo la variante correctamente")

                                    else:
                                        print(f"⚠️ No se encontró variante en Odoo para combinación {id_combination}")
                                else:
                                    print(f"⚠️ Revisar variante en Odoo para la combinacion {id_combination}") 

                else:
                    print(f'🔍🔍 El producto {nombre} ya existe en Odoo')
                    producto_odoo_id = search_product_odoo(id_product)
                    #Actualizamos el producto
                    Actualizar_producto = update_product(producto_odoo_id,nombre,id_product,referencia,precio_venta,obtener_id_categoria_odoo)
                    
                    #Actualizar productos sin variantes product.product
                    if existe_combination == 0:
                                obtener_id_product_product = get_product_product(producto_odoo_id)
                                actualizar_product_product = update_product_product(obtener_id_product_product, id_product, peso, barcode, referencia)


                    ##############################
                    # ACTUALIZAR VARIANTES (TAMBIÉN PARA PRODUCTOS EXISTENTES)
                    ##############################
                    if existe_combination != 0 and producto_odoo_id:
                        combinations = producto_detail.get('associations').get('combinations', [])
                        for combination in combinations:              #2. for es para combinaciones                            
                            id_combination = combination.get('id')                        
                            datos_combination = get_combination(id_combination)
                            
                            #  Usamos el ID del producto existente
                            id_padre_odoo = producto_odoo_id

                            product_option_values = datos_combination.get('associations', {}).get('product_option_values', [])
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
                    
                            # Ahora buscamos la variante en Odoo(product.product) que tenga EXACTAMENTE estos valores
                            if valores_odoo_ids: 
                                buscar_variante_odoo = search_variant_odoo(id_padre_odoo, valores_odoo_ids)
                                
                                #Buscamos el Id Odoo de la variante para luego pasarle ese valor a la plantilla product.template
                                if id_attribute_odoo == None:
                                    id_attribute_odoo = get_id_attribute_odoo(name_attribute)

                                #Obtenemos la plantilla (product.template) exactamente en el product.template.attribute.value por medio de su respectivo valor y nos traemos campos    
                                plantilla_product_attribute_value = get_product_template_product_attribute_value(id_padre_odoo, id_attribute_odoo, valores_odoo_ids)
                                #Obtenemos el id de esa unica plantilla
                                if plantilla_product_attribute_value:
                                    id_plantilla =  plantilla_product_attribute_value[0]['id']
                                    #Obtenemos en presta el precio de esa combinacion
                                    precio_combinacion = datos_combination.get('price')
                                    #Y ahora si, modificamos  
                                    modificar_precio_product_attribute_value = update_precio_product_attribute_value(id_plantilla, precio_combinacion)
                                    # Y actualizamos el product.template para que siga conservando su referencia en el producto padre
                                    config.models.execute_kw(
                                    config.db,
                                    config.uid,
                                    config.password,
                                    'product.template',
                                    'write',
                                    [[id_padre_odoo], {'default_code': referencia}]
                                )
                                else:
                                    print(f"⚠️ No se encontro plantilla del producto: {nombre}")
                        
                                if buscar_variante_odoo:
                                    datos_barcode = datos_combination.get('ean13')
                                    barcode = ''
                                    if len(str(datos_barcode)) > 1:
                                        barcode = datos_barcode
                                    else: 
                                        barcode = False
                                    # Preparar los datos de la combinación de PrestaShop
                                    datos_variante = {
                                        'weight': datos_combination.get('weight'),     # Peso
                                        'barcode': barcode, # Código de barras
                                        'x_studio_ps_id': id_combination,              # ID de PrestaShop
                                        'default_code': datos_combination.get('reference', '').rstrip()  # Referencia
                                    }                           
                                    # Actualizar la variante en Odoo
                                    actualizada_variante = update_variante(buscar_variante_odoo,datos_variante,nombre, id_combination, valores_odoo_ids)
                                    if actualizada_variante:
                                        print("🔃🔃 Se actualizo la variante correctamente")

                                else:
                                    print(f"⚠️ No se encontró variante en Odoo para combinación {id_combination}")
                            else:
                                print(f"⚠️ Revisar variante en Odoo para la combinacion {id_combination}") 

print(f"🎊🎉Proceso terminado: Productos creados en Odoo {len(subidos)}")