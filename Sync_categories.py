import config
import requests
import json
import base64

# ============================================
# FUNCIONES PRESTASHOP
# ============================================

def get_categories_id(): 
    try:
        url = f"{config.prestashop_url}/categories?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth=auth_tuple)
        
        if response.status_code == 200:
            data = response.json()
            category_list = data.get('categories', [])
            print(f"🎉🎉 Se obtuvieron: {len(category_list)}")
            return category_list
        else:
            print(f"❌❌ Error al obtener categorias {response.status_code}")
    except Exception as e:
        print(f'❌ Error en get_categories: {e}')
        return None
    

def get_categories_details(id):
    try:
        url = f"{config.prestashop_url}/categories/{id}?output_format=JSON"
        auth_tuple = (config.api_key, '')

        response = requests.get(url, auth=auth_tuple)
        
        if response.status_code == 200:
            data = response.json().get('category', {})
            print(f"🎉🎉 Detalles de la categoria obtenidos, Id: {id}")
            return data
        else:
            print(f"❌❌ Error al obtener Detalles de categoria {id}: {response.status_code}")
            return None
    except Exception as e:
        print(f'❌ Error en obtener categorias: {e}')
        return None    


# ============================================
# FUNCIONES ODOO
# ============================================

def get_category_by_ps_id(ps_id):
    """
    Busca si ya existe una categoría en Odoo con ese ID de PrestaShop
    Retorna el ID de Odoo si existe, None si no existe
    """
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.category',
            'search_read',
            [[['x_studio_p_id', '=', ps_id]]],
            {'fields': ['id', 'name', 'x_studio_p_id', 'parent_id']}
        )
        if result:
            return result[0]['id']
        return None
    except Exception as e:
        print(f"❌ Error buscando categoria PS ID {ps_id}: {e}")
        return None


def create_category(name, ps_id, parent_odoo_id=None):
    """
    Crea una categoría en Odoo
    """
    try:
        datos = {
            'x_studio_p_id': ps_id,
            'name': name
        }
        
        # Solo agregar parent_id si existe y no es categoría raíz
        if parent_odoo_id and ps_id not in [1, 2]:
            datos['parent_id'] = parent_odoo_id
        
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.category',
            'create',
            [datos]
        )
        
        if result:
            parent_info = f", Padre Odoo ID: {parent_odoo_id}" if parent_odoo_id else ""
            print(f"🥏🥏 Categoria creada: '{name}' (PS ID: {ps_id}, Odoo ID: {result}{parent_info})")
            return result
        else:
            print(f"❌❌ Error al crear categoria: {name}")
            return None        
    except Exception as e:
        print(f"❌ Error creando categoria ({name}): {e}")
        return None


def update_category_parent(odoo_id, parent_odoo_id):
    """
    Actualiza el parent_id de una categoría que ya existe
    """
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.category',
            'write',
            [[odoo_id], {'parent_id': parent_odoo_id}]
        )
        if result:
            print(f"🔃 Jerarquía actualizada para categoria Odoo ID: {odoo_id} -> Padre: {parent_odoo_id}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error actualizando jerarquía: {e}")
        return False


def update_categoria(id_odoo, nombre):
    try:
        result = config.models.execute_kw(
            config.db,
            config.uid,
            config.password,
            'product.category',
            'write',
            [[id_odoo], 
             {'name': nombre}]
        )
        if result:
            print(f"🔃 Nombre Actualizado: {nombre} -> Id Odoo: {id_odoo}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error actualizando jerarquía: {e}")
        return False





# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO SINCRONIZACIÓN DE CATEGORÍAS CON JERARQUÍA")
    print("="*60 + "\n")
    
    # Diccionario para mapear ID PrestaShop -> ID Odoo
    ps_to_odoo_map = {}
    
    # PASO 1: Obtener todas las categorías de PrestaShop
    categorias_id = get_categories_id()
    
    if not categorias_id:
        print("❌ No se obtuvieron categorías")
        exit()
    
    print(f'✅ Se obtuvieron {len(categorias_id)} categorías\n')
    
    # PASO 2: Obtener detalles de todas las categorías
    print("📋 Obteniendo detalles de todas las categorías...")
    todas_categorias = []
    
    for cat in categorias_id:
        cat_id = cat.get('id')
        detalles_categorias = get_categories_details(cat_id)
        if detalles_categorias:
            todas_categorias.append(detalles_categorias)
    
    # PASO 3: Ordenar por nivel de profundidad (level_depth)
    # Esto asegura que creamos primero las categorías padre
    todas_categorias.sort(key=lambda x: int(x.get('level_depth', 0)))
    print(f"✅ Categorías ordenadas por nivel de profundidad\n")
    
    # PASO 4: Crear categorías respetando la jerarquía
    print("🏗️  Creando/actualizando categorías en Odoo...\n")
    
    total_creadas = 0
    total_actualizadas = 0
    total_existentes = 0
    
    for detalles_categorias in todas_categorias:
        nombre_categoria = detalles_categorias.get('name')[0]['value']
        ps_id = int(detalles_categorias.get('id'))
        ps_parent_id = int(detalles_categorias.get('id_parent'))
        level_depth = detalles_categorias.get('level_depth')
        
        print(f"🔹 Procesando: '{nombre_categoria}' (PS ID: {ps_id}, Nivel: {level_depth}, Padre PS: {ps_parent_id})")
        
        # Verificar si ya existe en Odoo
        existing_odoo_id = get_category_by_ps_id(ps_id)
        
        # Buscar el ID del padre en Odoo
        parent_odoo_id = None
        if ps_parent_id in ps_to_odoo_map:
            parent_odoo_id = ps_to_odoo_map[ps_parent_id]
            print(f"   📁 Padre encontrado en mapa: PS ID {ps_parent_id} -> Odoo ID {parent_odoo_id}")
        
        if existing_odoo_id:
            # La categoría ya existe
            print(f"   ℹ️  Categoría ya existe en Odoo (ID: {existing_odoo_id})")
            ps_to_odoo_map[ps_id] = existing_odoo_id


            #Actualiza categoria con la de prestashop(solo actualiza su nombre)
            actualizar_categoria = update_categoria(existing_odoo_id, nombre_categoria)
            
            # Actualizar jerarquía si es necesario
            if parent_odoo_id and ps_id not in [1, 2]:
                update_category_parent(existing_odoo_id, parent_odoo_id)
                total_actualizadas += 1
            else:
                total_existentes += 1
        else:
            # Crear nueva categoría
            nuevo_odoo_id = create_category(nombre_categoria, ps_id, parent_odoo_id)
            if nuevo_odoo_id:
                ps_to_odoo_map[ps_id] = nuevo_odoo_id
                total_creadas += 1
        
        print()  # Línea en blanco para separar
    
    # RESUMEN FINAL
    print("="*60)
    print("📊 RESUMEN DE SINCRONIZACIÓN")
    print("="*60)
    print(f"✅ Total de categorías procesadas: {len(todas_categorias)}")
    print(f"🆕 Categorías nuevas creadas: {total_creadas}")
    print(f"🔄 Jerarquías actualizadas: {total_actualizadas}")
    print(f"📦 Categorías que ya existían: {total_existentes}")
    print(f"🎯 Total en el mapa PS->Odoo: {len(ps_to_odoo_map)}")
    print("="*60)