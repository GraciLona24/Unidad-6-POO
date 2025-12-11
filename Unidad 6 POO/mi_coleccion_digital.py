import os
import csv
import pickle
import sys
from typing import Dict, Any

TXT_FILE = 'collection.txt'
BIN_FILE = 'stats.bin'



def init_files():
    """Crear los archivos si no existen. Si existen pero están vacíos, dejar vacíos.
    También inicializa el archivo binario con un diccionario vacío si no existe.
    """
    try:
        if not os.path.exists(TXT_FILE):
            with open(TXT_FILE, 'w', encoding='utf-8') as f:
                f.write('id|nombre|categoria|anio|creador|calificacion\n')

        if not os.path.exists(BIN_FILE):
            with open(BIN_FILE, 'wb') as bf:
                pickle.dump({}, bf)
    except OSError as e:
        print(f"Error al crear archivos: {e}")
        sys.exit(1)


def get_next_id() -> int:
    """Obtiene el próximo ID incremental leyendo el archivo de texto """
    try:
        with open(TXT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            records = [ln.strip() for ln in lines if ln.strip()]
            if len(records) <= 1:
                return 1
            last = records[-1]
            parts = last.split('|')
            try:
                return int(parts[0]) + 1
            except Exception:
                ids = []
                for r in records[1:]:
                    try:
                        ids.append(int(r.split('|')[0]))
                    except Exception:
                        continue
                return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        raise


def save_item_text(item: Dict[str, Any]):
    """Guarda un elemento en el archivo de texto (append)."""
    try:
        with open(TXT_FILE, 'a', encoding='utf-8') as f:
            line = f"{item['id']}|{item['nombre']}|{item['categoria']}|{item['anio']}|{item['creador']}|{item['calificacion']}\n"
            f.write(line)
    except OSError as e:
        print(f"Error al escribir en {TXT_FILE}: {e}")


def read_all_items() -> list:
    """Lee y devuelve todos los items del archivo de texto como lista de dicts """
    items = []
    try:
        with open(TXT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            
            rows = list(reader)
            if not rows:
                return items
            start = 0
            if rows[0] and 'nombre' in ''.join(rows[0]).lower():
                start = 1
            for r in rows[start:]:
                if not r or len(r) < 6:
                    continue
                try:
                    items.append({
                        'id': int(r[0]),
                        'nombre': r[1],
                        'categoria': r[2],
                        'anio': int(r[3]),
                        'creador': r[4],
                        'calificacion': float(r[5])
                    })
                except ValueError:
                    print(f"Advertencia: línea con formato inválido ignorada: {r}")
                    continue
    except FileNotFoundError:
        raise
    return items


def search_item_by_name(name: str) -> list:
    """Busca items cuyo nombre contenga el texto dado (case-insensitive) """
    try:
        items = read_all_items()
    except FileNotFoundError:
        print(f"Archivo {TXT_FILE} no encontrado ")
        return []
    name = name.strip().lower()
    if not name:
        raise ValueError('Entrada vacía para búsqueda')
    matches = [it for it in items if name in it['nombre'].lower()]
    return matches


def load_stats() -> Dict[int, Dict[str, Any]]:
    """Carga el diccionario de stats desde el archivo binario """
    try:
        with open(BIN_FILE, 'rb') as bf:
            try:
                data = pickle.load(bf)
                if not isinstance(data, dict):
                    print("Advertencia: datos binarios inesperados. Re-inicializando ")
                    return {}
                return data
            except EOFError:
                return {}
    except FileNotFoundError:
        raise
    except (OSError, pickle.UnpicklingError) as e:
        print(f"Error al leer {BIN_FILE}: {e}")
        return {}


def save_stats(stats: Dict[int, Dict[str, Any]]):
    """Guarda el diccionario de stats en el archivo binario."""
    try:
        with open(BIN_FILE, 'wb') as bf:
            pickle.dump(stats, bf)
    except OSError as e:
        print(f"Error al escribir en {BIN_FILE}: {e}")


def add_stats_for_id(item_id: int, stats_values: Dict[str, Any]):
    """Añade o actualiza estadísticas para un ID dado."""
    try:
        stats = load_stats()
    except FileNotFoundError:
        print(f"Archivo {BIN_FILE} no encontrado. Intentando crear uno nuevo ")
        stats = {}
    stats[item_id] = stats_values
    save_stats(stats)


def input_nonempty(prompt: str) -> str:
    s = input(prompt).strip()
    if not s:
        raise ValueError('Entrada vacía no permitida')
    return s


def add_item_interactive():
    """Interfaz para agregar un nuevo elemento (texto + stats binarios) """
    try:
        nombre = input_nonempty('Nombre: ')
        categoria = input_nonempty('Categoría: ')
        anio_s = input_nonempty('Año (ej. 2021): ')
        try:
            anio = int(anio_s)
        except ValueError:
            raise ValueError('Año inválido. Debe ser un número entero ')
        creador = input_nonempty('Creador: ')
        cal_s = input_nonempty('Calificación (0.0 - 10.0): ')
        try:
            cal = float(cal_s)
        except ValueError:
            raise ValueError('Calificación inválida. Debe ser número decimal ')
        if not (0.0 <= cal <= 10.0):
            raise ValueError('Calificación debe estar entre 0.0 y 10.0')

        
        new_id = get_next_id()
        item = {
            'id': new_id,
            'nombre': nombre,
            'categoria': categoria,
            'anio': anio,
            'creador': creador,
            'calificacion': cal
        }
        save_item_text(item)

        print('\nAhora agrega estadísticas numéricas (se guardarán en binario):')
        poder_s = input_nonempty('Nivel de poder (entero): ')
        try:
            poder = int(poder_s)
        except ValueError:
            raise ValueError('Nivel de poder inválido. Debe ser entero ')
        popularidad_s = input_nonempty('Popularidad (0-100): ')
        try:
            popularidad = int(popularidad_s)
        except ValueError:
            raise ValueError('Popularidad inválida. Debe ser entero ')
        vistas_s = input_nonempty('Número de vistas (entero): ')
        try:
            vistas = int(vistas_s)
        except ValueError:
            raise ValueError('Vistas inválido. Debe ser entero ')
        rareza_s = input_nonempty('Rareza (1-100): ')
        try:
            rareza = int(rareza_s)
        except ValueError:
            raise ValueError('Rareza inválida. Debe ser entero ')
        if not (1 <= rareza <= 100):
            raise ValueError('Rareza debe estar entre 1 y 100')

        stats = {
            'poder': poder,
            'popularidad': popularidad,
            'vistas': vistas,
            'rareza': rareza
        }
        add_stats_for_id(new_id, stats)
        print(f"Elemento '{nombre}' agregado con ID {new_id}.\n")

    except ValueError as ve:
        print(f"Entrada inválida: {ve}")
    except FileNotFoundError as fe:
        print(f"Error: archivo no encontrado: {fe}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al agregar elemento: {e}")
    finally:
        pass


def show_collection():
    try:
        items = read_all_items()
        if not items:
            print('Colección vacía')
            return
        print('\n===== COLECCIÓN COMPLETA =====')
        for it in items:
            print(f"ID: {it['id']} | Nombre: {it['nombre']} | Categoria: {it['categoria']} | Año: {it['anio']} | Creador: {it['creador']} | Calificación: {it['calificacion']}")
        print('')
    except FileNotFoundError:
        print(f"Archivo {TXT_FILE} no encontrado ")


def search_and_show():
    try:
        query = input_nonempty('Buscar por nombre: ')
        matches = search_item_by_name(query)
        if not matches:
            print('No se encontraron coincidencias')
            return
        for it in matches:
            print(f"ID: {it['id']} | Nombre: {it['nombre']} | Categoria: {it['categoria']} | Año: {it['anio']} | Creador: {it['creador']} | Calificación: {it['calificacion']}")
    except ValueError as ve:
        print(f"Entrada inválida: {ve}")


def show_binary_for_item():
    """Permite ver los datos binarios asociados a un ítem por nombre o ID """
    try:
        choice = input('Buscar por (1) Nombre o (2) ID ? [1/2]: ').strip()
        stats = load_stats()
        if choice == '1':
            name = input_nonempty('Nombre: ')
            matches = search_item_by_name(name)
            if not matches:
                print('No se encontraron items con ese nombre ')
                return
            for it in matches:
                sid = it['id']
                st = stats.get(sid)
                print(f"\nID {sid} - {it['nombre']}")
                if st:
                    for k, v in st.items():
                        print(f"  {k}: {v}")
                else:
                    print('  No hay datos binarios para este ID ')
        elif choice == '2':
            id_s = input_nonempty('ID: ')
            try:
                iid = int(id_s)
            except ValueError:
                raise ValueError('ID inválido ')
            st = stats.get(iid)
            if st:
                print(f"Datos binarios para ID {iid}:")
                for k, v in st.items():
                    print(f"  {k}: {v}")
            else:
                print('No hay datos binarios para ese ID ')
        else:
            print('Opción inválida.')
    except FileNotFoundError:
        print(f"Archivo binario {BIN_FILE} no encontrado ")
    except ValueError as ve:
        print(f"Entrada inválida: {ve}")
    except Exception as e:
        print(f"Error al leer datos binarios: {e}")



def seed_if_empty():
    """Si el archivo de texto solo tiene header o está vacío, crea 5 registros de ejemplo """
    try:
        items = read_all_items()
    except FileNotFoundError:
        items = []
    if len(items) >= 5:
        return
    print('Inicializando colección con 5 ejemplos...')
    ejemplos = [
        {'nombre': 'Aoi', 'categoria': 'Personaje', 'anio': 2020, 'creador': 'Autor X', 'calificacion': 8.5,
         'stats': {'poder': 85, 'popularidad': 70, 'vistas': 1200, 'rareza': 25}},
        {'nombre': 'Bisho', 'categoria': 'Personaje', 'anio': 2018, 'creador': 'Estudio Y', 'calificacion': 9.0,
         'stats': {'poder': 92, 'popularidad': 85, 'vistas': 5400, 'rareza': 12}},
        {'nombre': 'Crescent Song', 'categoria': 'Canción', 'anio': 2021, 'creador': 'Banda Z', 'calificacion': 7.5,
         'stats': {'poder': 60, 'popularidad': 65, 'vistas': 2300, 'rareza': 40}},
        {'nombre': 'Drako Lance', 'categoria': 'Arma', 'anio': 2016, 'creador': 'Forjador K', 'calificacion': 8.8,
         'stats': {'poder': 98, 'popularidad': 55, 'vistas': 800, 'rareza': 5}},
        {'nombre': 'Eureka', 'categoria': 'Libro', 'anio': 2019, 'creador': 'Escritor Q', 'calificacion': 9.2,
         'stats': {'poder': 50, 'popularidad': 90, 'vistas': 7600, 'rareza': 30}},
    ]
    starting_id = get_next_id()
    for i, ej in enumerate(ejemplos):
        nid = starting_id + i
        item = {
            'id': nid,
            'nombre': ej['nombre'],
            'categoria': ej['categoria'],
            'anio': ej['anio'],
            'creador': ej['creador'],
            'calificacion': ej['calificacion']
        }
        save_item_text(item)
        add_stats_for_id(nid, ej['stats'])
    print('Ejemplos creados.\n')


def main_menu():
    init_files()
    try:
        seed_if_empty()
    except Exception:
        pass

    while True:
        print('===== MI COLECCIÓN DIGITAL =====')
        print('1. Agregar elemento')
        print('2. Mostrar colección completa')
        print('3. Buscar elemento por nombre')
        print('4. Mostrar datos binarios')
        print('5. Salir')
        opc = input('Seleccione una opción [1-5]: ').strip()
        if opc == '1':
            add_item_interactive()
        elif opc == '2':
            show_collection()
        elif opc == '3':
            search_and_show()
        elif opc == '4':
            show_binary_for_item()
        elif opc == '5':
            print('Saliendo ¡Hasta luego!')
            break
        else:
            print('Opción inválida. Intente de nuevo')


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print('\nInterrumpido por el usuario Saliendo...')
    except Exception as e:
        print(f"Error no controlado: {e}")
