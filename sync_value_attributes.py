import config
import requests
import json
import base64


from get_values_attributes import get_values, get_attributes, create_attribute_odoo, create_value_odoo, get_id_attribute_odoo,get_value_id_odoo,get_value_id_ps_odoo,get_variantes_odoo,write_variantes_odoo, get_attribute_p_id_odoo


def get_attributes_all():
    try:
        url = f"{config.prestashop_url}/product_options/?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth= auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('product_options')
            print(f"🎉🎉 attributo obtenidos")
            return data
        else:
            print(f"❌❌Error al obtener Detalles del attribute {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en get_attribute: {e}')
        return None
    

def update_attribute(id_odoo, name):
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.attribute',
            'write',
            [[id_odoo], {'name': name}]
        )
        if result:
            print(f'🔃 Nombre del Atributo Actualizado : {name}')
            return result
        else:
            return None
    except Exception as e:
        print(f'❌ Error en Actualizar: {e}')
        return None


def update_value(valor_id,name_value): 
    try:
        valor_id_int = int(valor_id)
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.attribute.value',
            'write',
            [[valor_id_int], {'name': name_value}]
        )
        if result:
            print(f'🔃 Nombre del valor Actualizado : {name_value}')
            return result
        else:
            return None
    except Exception as e:
        print(f'❌ Error en Actualizar: {e}')
        return None

#______________________________________________________________________________________________________






if __name__=="__main__":
    total_atributos_creados = 0
    total_valores_creados = 0
    
    #Mira si tiene VALORES y las obtiene por producto
    obtener_atributos = get_attributes_all()
    for atributo in obtener_atributos:
        atributo_id = atributo.get('id')
        #Obtenemos_detalle de cada atributo
        obtener_detalles_atributo = get_attributes(atributo_id)
        if obtener_detalles_atributo:
            name_attribute = obtener_detalles_atributo.get('name')[0].get('value')
            #miramos si el atributo ya existe en Odoo
            id_prestashop_attribute_odoo = get_attribute_p_id_odoo(atributo_id)
            #Si el atributo id prestashop es diferente al id de prestashop de Odoo lo creamos
            if atributo_id != id_prestashop_attribute_odoo:
                upload_attribute_odoo = create_attribute_odoo(name_attribute, atributo_id)
                total_atributos_creados += 1
            else:
                print('🔍El atributo ya existe en Odoo')

            #Actualizamos el nombre del Atributo en Odoo si es que ya existe
            #Creamos una funcion para EXTRAER el Id del atributo de Odoo x medio del name atributo
            id_attribute_odoo = get_id_attribute_odoo(name_attribute)
            if id_attribute_odoo:
                actualizar_nombre_atributo = update_attribute(id_attribute_odoo, name_attribute)

        obtener_valores_atributo = obtener_detalles_atributo.get('associations').get('product_option_values')
        for valor in obtener_valores_atributo:
            valor_id = valor.get('id')        
            valor_id_ps_odoo = get_value_id_ps_odoo(valor_id)
            detalles_valor = get_values(valor_id)
            id_valor_ps = detalles_valor.get('id')
            name_value = detalles_valor.get('name')[0].get('value')
            if valor_id_ps_odoo != id_valor_ps:
                #Creamos los VALORES de ese atributo en PRODUCT.ATTRIBUTE.VALUE
                if id_attribute_odoo:
                    if detalles_valor:                        
                        valor_creado = create_value_odoo(id_attribute_odoo,name_value, id_valor_ps)
                        if valor_creado:
                            print(f"✅✅ VALOR CREADO: '{name_value}' para atributo '{name_attribute}' (ID PS: {id_valor_ps})") 
                    total_valores_creados += 1
            else:
                print(f'🔍El valor ya existe en Odoo {valor_id}')

            #Actulizamos el nombre del Valores en Odoo

            actualizar_nombre_valor = update_value(valor_id,name_value )
                        
                                       
print(f"🎯 Total de atributos creados en Odoo: {total_atributos_creados}") 






    