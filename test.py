import config
import requests
import re


def get_orders_ps(): 
    try:
        url = f"{config.prestashop_url}/orders?output_format=JSON&display=full&filter[date_add]=[2025-11-12%2000:00:00,2025-11-14%2000:00:00]&date=1"                       
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            print(f"🎉🎉 Se obtuvieron: {len(orders )} ordenes")
            return orders
        else:
            print(f"❌❌Error al obtener ordenes {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_orders_ps: {e}')
        return None


def get_order_detail_ps(id): 
    try:
        url = f"{config.prestashop_url}/orders/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('order')
            print(f"🎉🎉 Detalle de la orden obtenida ID: {id}")
            return orders
        else:
            print(f"❌❌Error orden {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_detail_ps: {e}')
        return None


def get_customer_data(id):
    try:
        url = f"{config.prestashop_url}/customers/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            cliente = data.get('customer')
            print(f"🎉🎉 Cliente obtenido: {id}")
            return cliente
        else:
            print(f"❌❌Error obteniendo cliente {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_customer_data: {e}')
        return None


def get_address(id):
    try:
        url = f"{config.prestashop_url}/addresses/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address')
            print(f"🎉🎉 Direccion Obtenida: {id}")
            return address
        else:
            print(f"❌❌Error obteniendo direccion {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_addres: {e}')
        return None


def get_country(id):
    try:
        url = f"{config.prestashop_url}/countries/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('country')
            print(f"🎉🎉 pais obtenido: {id}")
            return address
        else:
            print(f"❌❌Error obteniendo pais {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_country: {e}')
        return None


def search_client_odoo(email):
    try:
        existing_client = config.models.execute_kw(
            config.db, 
            config.uid, 
            config.password, 
            'res.partner', 
            'search', 
            [[
                ['email','=', email]
            ]],
        )
        if existing_client:
            print(f"👤Cliente en Odoo con ID: {existing_client}")
            return existing_client
        else:
            print(f"🔭 Cliente no esta en Odoo")
            return None        
    except Exception as e:
        print(f'❌ search_client_odoo: {e}')
        return None


def create_client_odoo(odoo):
    try:
        partner_up = config.models.execute_kw(
            config.db, 
            config.uid, 
            config.password, 
            'res.partner', 
            'create', 
            [odoo]
        )
        if partner_up:
            print(f"👤 Se creo con exito el cliente en Odoo Id: {partner_up}")
            return partner_up
        else:
            print("❌ Error al crear cliente")
            return None        
    except Exception as e:
        print(f'❌ Error en create_client: {e}')
        return None


def update_client(cliente):
    try:
        id  = cliente[0]
        datos_odoo = {
                    'name':       nombre,
                    'email':      email,
                    'phone':      phone,
                    'street':     address1,
                    'street2':    address2,
                    'city':       ciudad,
                    'zip':        postcode,
                    'country_id': id_pais_odoo[0],                    
                    'vat':        vat_procesado
        }
        existing_client = config.models.execute_kw(
            config.db, 
            config.uid, 
            config.password, 
            'res.partner', 
            'write', 
            [[id], datos_odoo],
        )
        if existing_client:
            print(f"🔃🔃----Cliente actualizado en Odoo con ID: {id}")
            return existing_client
        else:
            print(f"🔭 No se puedo actualizar el cliente con ID: {id} ")
            return None        
    except Exception as e:
        print(f'❌ update_cliente: {e}')
        return None


def get_country_odoo_by_name(code):
    try:
        country_id = config.models.execute_kw(config.db,
            config.uid, 
            config.password,
            'res.country', 
            'search', 
            [[('code', '=', code)]], 
            {'limit': 1}
            )
        if country_id:
            return country_id
        else:
            return False        
    except Exception as e:
        print(f'❌ get_country_odoo_by_name: {e}')
        return None


def search_order_odoo_by_ps_id(id):
    try:
        existing_order = config.models.execute_kw(config.db,
            config.uid, 
            config.password,
            'sale.order', 
            'search', 
            [[('x_studio_p_id', '=', id)]], 
            {'limit': 1}
            )
        if existing_order:
            return existing_order
        else:
            return False        
    except Exception as e:
        print(f'❌ search_order_odoo_by_ps_id: {e}')
        return None


def get_product_odoo_by_id(product_id, combinacion):
    try:
        #1. Busqueda por el producto padre
        domain = [['x_studio_ps_id', '=', combinacion]]
        existing_product = config.models.execute_kw(config.db,
            config.uid, 
            config.password,
            'product.product', 
            'search', 
            [domain], 
            {'limit': 1}
            )
        if existing_product:
            return existing_product
        else:
            domain = [['x_studio_p_id', '=', product_id]]
            existing_product = config.models.execute_kw(config.db,
            config.uid, 
            config.password,
            'product.product', 
            'search', 
            [domain], 
            {'limit': 1}
            )
        if existing_product:
            return existing_product        
    except Exception as e:
        print(f'❌ get_product_odoo_by_id: {e}')
        return None
    

def odoo_send_chat(message):
    try:
        # Enviar mensaje al canal
        message_id = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'discuss.channel',
            'message_post',
            [gc_canal_log],
            {
                'body': message,
                'message_type': 'comment',
                'subtype_xmlid': 'mail.mt_comment',
            }
        )
        return message_id
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        return None


def search_tag_odoo_by_name(metodo_pago):
    try:
        tag_ids = config.models.execute_kw(
                config.db,
                config.uid,
                config.password,
                'crm.tag',        # Modelo real
                'search',
                [[('name', '=', metodo_pago)]],
                {'limit': 1}
            )
        if tag_ids:
            return tag_ids[0]
        if not tag_ids:
            tag_ids = config.models.execute_kw(
                config.db,
                config.uid,
                config.password,
                'crm.tag',        
                'create',
                [{'name': metodo_pago}]
            )
        if tag_ids:
            return tag_ids[0]
    except Exception as e:
        print(f'❌ search_tag_odoo_by_name: {e}')
        return None
    

#########FUNCION DE PRUEBA#######
def get_order_detail_odoo(new_order_id):
    try:
        order = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'sale.order',
            'read',
            [[new_order_id]],
            {'fields': ['name', 'x_studio_p_total', 'partner_id', 'amount_total']}
        )
        if order:
            print(f"🎉🎉 Detalle de la orden en Odoo ID: {new_order_id}")
            return order
        else:
            print(f"❌❌Error orden en Odoo {new_order_id}")
    except Exception as e:
        print(f'❌ Error en get_order_detail_odoo: {e}')
        return None
#################################


#_________________________________________ORDERS________________________________________________
gc_canal_log    = [10]
obtener_ordenes = get_orders_ps()
if obtener_ordenes:
    pedidos_cargados = 0
    for id in obtener_ordenes:
        id_orden = id.get('id')
        producto_no_encontrado = False # <---Bandera
        #1. Buscamos si el pedido ya esta en Odoo
        id_pedido_ps = search_order_odoo_by_ps_id(id_orden)
        #Si el pedido no esta: haremos el flujo de todo lo que representa la creacion del pedido 
        if not id_pedido_ps:
            order_detail = get_order_detail_ps(id_orden)
            if order_detail:
                num_factura = order_detail.get('invoice_number')
                metodo_pago = order_detail.get('payment')
                referencia =  order_detail.get('reference')
                id_cliente =  order_detail.get('id_customer')
                id_adresses = order_detail.get('id_address_delivery')
                shipping_tax = order_detail.get('total_shipping_tax_incl')
                total_paid_taxes = order_detail.get('total_paid_tax_incl')
                descuentos   =  order_detail.get('total_discounts', "0.0")

                lineas_productos = order_detail.get('associations',{}).get('order_rows')
                
                #Obtener direccion cliente ->datos para res.partner
                direccion = get_address(id_adresses)
                if direccion:
                    ciudad =   direccion.get('city')
                    postcode = direccion.get('postcode')
                    phone =    direccion.get('phone')
                    mobile =   direccion.get('phone_mobile')
                    address1 = direccion.get('address1')
                    address2 = direccion.get('address2')
                    vat =      direccion.get('vat_number')
                    #condicion vat si contiene formato incorrecto
                    vat_filtrado = vat.replace(" ","")
                    vat_limpio = re.sub(r'[^A-Za-z0-9]', '', vat_filtrado)
                    vat_final = vat_limpio[:13]
                    tiene_numero = any(char.isdigit() for char in vat_final)
                    vat_procesado =  vat_final if tiene_numero else False
    
                    id_pais =  direccion.get('id_country')
                    obtener_pais = get_country(id_pais)
                    if obtener_pais:
                        codigo_pais = obtener_pais.get('iso_code')
                        name_country = obtener_pais.get('name')[0]['value']       
                        id_pais_odoo = get_country_odoo_by_name(codigo_pais)
                    else:
                        id_pais_odoo = False
                else:
                    print("⚠️No hay datos en la variable direccion")

                #Obtener datos del cliente en PRESTAHSOP para luego pasarlos a ->res.partner Odoo
                datos_cliente = get_customer_data(id_cliente)
                if datos_cliente:
                    email = datos_cliente.get('email')
                    nombre = datos_cliente.get('firstname')
                else:
                    print("⚠️No hay datos en la variable datos_cliente")
                

                #2. Buscar cliente en Odoo, si no esta: Lo Creamos y si esta: Lo Actualizamos
                cliente_Odoo = search_client_odoo(email)
                if not cliente_Odoo:
                #Datos para Odoo
                    datos_odoo = {
                        'name':       nombre,
                        'email':      email,
                        'phone':      phone,
                        'street':     address1,
                        'street2':    address2,
                        'city':       ciudad,
                        'zip':        postcode,
                        'country_id': id_pais_odoo[0] if id_pais_odoo else False, #SI id_pais_odoo SOLO si es True, intenta coger el primer elemento [0].
                        'vat':        vat_procesado,
                }    
                    subir_cliente_odoo = create_client_odoo(datos_odoo)
                    if subir_cliente_odoo:
                        cliente_Odoo = [subir_cliente_odoo]

                else:
                    actualizar_cliente = update_client(cliente_Odoo)

                
                #Lectura de los productos de las lineas del pedido
                order_lines_ps = []
                for linea in lineas_productos:
                    product_id          =  linea.get('product_id')             #Producto padre
                    combinacion         = linea.get('product_attribute_id')    #Producto Combinacion
                    cantidad            = linea.get('product_quantity', 1)     #Cantidad
                    nombre_producto     = linea.get('product_name')            #Producto Nombre
                    referencia_product  = linea.get('product_reference')       #Producto referencia
                    referencia_product  = linea.get('product_ean13": ')        #Codebar
                    price               = linea.get('unit_price_tax_excl', 0.0)      #Precio unitario

                    #por cada linea buscar ese producto por ID PRESTASHOP o referencia 
                    #el ID del producto ODOO 
                    obtener_producto_odoo = get_product_odoo_by_id(product_id, combinacion)
                    if obtener_producto_odoo:
                       #preparar las lineas dentro del pedido
                        order_lines_ps.append({
                                'product_uom_qty':  cantidad,
                                'price_unit':       float(price),
                                'name':             nombre_producto,
                                'product_id':       obtener_producto_odoo[0],                                  

                        })
                        msg_log = f"✅🆙 {nombre_producto} - {product_id } - {combinacion}"
                        mensaje_canal = odoo_send_chat(msg_log)
                    #Si no encuentro el producto:   
                    else:
                        producto_no_encontrado = True
                        order_lines_ps.append({
                                'product_uom_qty':  cantidad,
                                'price_unit':       float(price),
                                'name':             nombre_producto
                        })
                        msg_log = f"❌ {nombre_producto} - {product_id } - {combinacion}"
                        mensaje_canal = odoo_send_chat(msg_log)
                
                if shipping_tax:
                    order_lines_ps.append({
                        'product_uom_qty':  1,
                        'price_unit':       float(shipping_tax),
                        'product_id':       19375,
                        'tax_ids':          False                                 
                    })

                if descuentos > "0":
                    order_lines_ps.append({
                        'product_uom_qty':  1,
                        'price_unit':       str(-float(descuentos)),
                        'product_id':       19374,
                        'tax_ids':          False                               
                    })


                #3. Crear el pedido en Odoo
                if producto_no_encontrado:
                    estado_pedido = 'draft' 
                else:
                    estado_pedido = 'sale'   
                
                etiqueta_metodo_pago = search_tag_odoo_by_name(metodo_pago)
                
                od_sales_order = {
                    'partner_id':          cliente_Odoo[0],
                    'client_order_ref':    referencia,
                    'order_line':          [(0, 0, vals) for vals in order_lines_ps],  #lineas
                    'x_studio_p_id':       id_orden,
                    'require_signature':   False,
                    'team_id':             1,
                    'x_studio_p_total':    total_paid_taxes,
                    'state':               estado_pedido,
                    'tag_ids':             [(6, 0 , [etiqueta_metodo_pago])] if etiqueta_metodo_pago else [],       
                }   
                new_order_id = config.models.execute_kw(config.db, config.uid, config.password, 'sale.order', 'create', [od_sales_order])
                if new_order_id:
                    pedidos_cargados = pedidos_cargados + 1
                    print(f"🛒 Pedido creado en Odoo con ID: {new_order_id} del pedido PrestaShop ID: {id_orden}")
                    #FUNCION EN PRUEBA
                    obtener_orden_subida = get_order_detail_odoo(new_order_id)
                    total_amount_invoicing = obtener_orden_subida[0].get('amount_total') 
                    diferencia = abs(total_amount_invoicing - float(total_paid_taxes))
                    update = {'state' : 'draft'}
                    if diferencia >= 2:                        
                        config.models.execute_kw(config.db, config.uid, config.password, 'sale.order', 'write',[[new_order_id], update])
                        msg_log = f"❌ Odoo:{total_amount_invoicing} - PS:{total_paid_taxes} - DIFERENCIA:{diferencia:.2f}"
                        mensaje_canal = odoo_send_chat(msg_log)
                    else:
                        continue
        else:
            print(f"🔭 El pedido ya existe en Odoo con ID: {id_pedido_ps} del pedido PrestaShop ID: {id_orden}")
print(f'🧩🆙👤🪀 Se cargaron {pedidos_cargados} pedidos a Odoo satisfactoriamente')






