import config
import requests


def get_orders_ps(): 
    try:
        url = f"{config.prestashop_url}/orders?output_format=JSON&display=full&filter[date_add]=[2025-10-23%2000:00:00,2025-10-24%2000:00:00]&date=1"
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
                    'country_id': name_country,
                    'vat':        vat
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



#_________________________________________ORDERS________________________________________________

obtener_ordenes = get_orders_ps()
if obtener_ordenes:
    for id in obtener_ordenes:
        id_orden = id.get('id')

        #1. Buscamos el pedido si ya esta en Odoo
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
                total_paid_taxes = order_detail.get('total_paid_tax_incl')
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
                    id_pais =  direccion.get('id_country')
                    obtener_pais = get_country(id_pais)
                    if obtener_pais:
                        codigo_pais = obtener_pais.get('iso_code')
                        name_country = obtener_pais.get('name')[0]['value']       
                        id_pais_odoo = get_country_odoo_by_name(codigo_pais)
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
                        'country_id': id_pais_odoo[0],
                        'vat':        vat
                }    
                    subir_cliente_odoo = create_client_odoo(datos_odoo)
                else:
                    actualizar_cliente = update_client(cliente_Odoo)

                
                #Lectura de los productos de las lineas del pedido
                for linea in lineas_productos:
                    product_id          =  linea.get('id')                     #Producto padre
                    combinacion         = linea.get('product_attribute_id')    #Producto Combinacion
                    cantidad            = linea.get('product_quantity')        #Cantidad
                    nombre_producto     = linea.get('product_name')            #Producto Nombre
                    referencia_product  = linea.get('product_reference')       #Producto referencia
                    referencia_product  = linea.get('product_ean13": ')        #Codebar

                    #por cada linea buscar ese producto por ID PRESTASHOP o referencia 
                    #el ID del producto ODOO
                    obtener_producto = get_product_odoo_by
                    







       


            # if lineas_productos:
            #     for linea_producto in lineas_productos:   





