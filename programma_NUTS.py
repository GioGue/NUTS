
#programma per vedere in che NUTS si trova un indirizzo
#controllare di avere tutti i package installati

#modificare il path del file da leggere
# scaricare il file zip ed estrarlo nel formato geojeson:
# https://gisco-services.ec.europa.eu/distribution/v2/nuts/download/#nuts24

import json
from shapely.geometry import Polygon, Point
import requests
from pyproj import Transformer

def count_levl_code_occurrences(file_path):
    try:
        # Apri e carica il file GeoJSON
        with open(file_path, 'r', encoding='utf-8') as file:
            geojson_data = json.load(file)

        # Controlla se il file è un FeatureCollection
        if geojson_data.get('type') == 'FeatureCollection':
            # Inizializza il conteggio per ogni valore di LEVL_CODE
            levl_counts = {0: 0, 1: 0, 2: 0, 3: 0}

            # Itera su tutte le feature
            for feature in geojson_data.get('features', []):
                properties = feature.get('properties', {})
                levl_code = properties.get('LEVL_CODE')

                # Verifica se LEVL_CODE è tra quelli di interesse
                if levl_code in levl_counts:
                    levl_counts[levl_code] += 1
                #stampa di prova per vedere quali sono i livel 1
                #if levl_code == 1:
                #    print(properties.get('NUTS_NAME'))
                 #   print(properties.get('NUTS_ID'))
                  #  print(levl_counts[1])
                   # print("")

            # Stampa il risultato
            for key, value in levl_counts.items():
                print(f"Numero di record con LEVL_CODE = {key}: {value}")

        else:
            print("Il file non è un FeatureCollection valido.")

    except FileNotFoundError:
        print(f"Errore: Il file '{file_path}' non è stato trovato.")
    except json.JSONDecodeError:
        print(f"Errore: Il file '{file_path}' non è un JSON valido.")
    except Exception as e:
        print(f"Si è verificato un errore inaspettato: {e}")

def address_to_coordinates_4326(address):
    """Convert an address to latitude and longitude (EPSG:4326) using OpenStreetMap's Nominatim API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'apiforuniversityproject' #esempio nome user agent per non avere problemi con la request
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            lon = float(data[0]['lon'])
            lat = float(data[0]['lat'])
            return (lon, lat)
        else:
            raise ValueError("Address not found.")
    else:
        raise ConnectionError(f"Failed to connect to geocoding service. Status code: {response.status_code}")

#il file utilizzato con i poligoni dei NUTS usa versione EPSG: 3857 (piano cartesiano)
def transform_coordinates_4326_to_3857(coords_4326):
    """Transform coordinates from EPSG:4326 to EPSG:3857."""
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    coords_3857 = transformer.transform(coords_4326[0], coords_4326[1])
    return coords_3857


def load_geojson(file_path):
    """Load and parse the GeoJSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def is_point_in_polygon(point, polygon_coords):
    """Check if a point is inside a polygon."""
    if not polygon_coords:
        return False

    # Create a Shapely Polygon object
    polygon = Polygon(polygon_coords[0])  # The first list contains the outer ring

    # Create a Shapely Point object
    point = Point(point)
    # Check if the point is inside the polygon
    return polygon.contains(point)

def find_features_containing_point(geojson_data, point):
    """Find all features where the point is inside the polygon."""
    results = []

    if geojson_data.get('type') == 'FeatureCollection':
        features = geojson_data.get('features', [])
        for feature in features:
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})

            if geometry.get('type') == 'Polygon':
                polygon_coords = geometry.get('coordinates', [])

                if is_point_in_polygon(point, polygon_coords):
                    # Retrieve NUTS_ID and LEVL_CODE
                    nuts_id = properties.get('NUTS_ID', 'Unknown')
                    levl_code = properties.get('LEVL_CODE', 'Unknown')
                    results.append((nuts_id, levl_code))

    return results

def main():

    # Path to your GeoJSON file
    #adrebbe effettuata una lettura del file CSV riga per riga per ottenere l'indirizzo corrente
    #si usa un indirizzo di esempio
    address = "Corso Duca degli Abruzzi, 24. Torino 10129 Piemonte Italy"
    try:
        # Step 1: Convert address to coordinates (EPSG:4326)
        #gli indirzzi sono di facile trasformazione con richieste HTTP in formato 4326 (ma non 3857)
        #il formato 4326 invece non è adatto per convertire verificare se un punto si trova in un poligono
        coords_4326 = address_to_coordinates_4326(address)
        #print(f"Coordinates (EPSG:4326): {coords_4326}")

        # Step 2: Transform coordinates to EPSG:3857
        #il file utilizzato con i poligoni dei NUTS usa versione EPSG: 3857 (piano cartesiano)
        coords_3857 = transform_coordinates_4326_to_3857(coords_4326)
        #print(f"Coordinates (EPSG:3857): {coords_3857}")
    except (ValueError, ConnectionError) as e:
        print(e)

    #ricavo il path dove si trova il file per le informazioni dei NUTS
    #usare "r" prima dell'indirizzo per evitare leggere correttamente "\"
    #file_path = r"PATH_ANTECEDENTE_AL_FILE\NUTS_RG_01M_2024_3857.geojson"
    file_path = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS_RG_20M_2024_3857.geojson" #pathesempio
    #prova conteggio record
    #count_records_in_geojson(file_path1)
    count_levl_code_occurrences(file_path)

    # Load the GeoJSON file
    geojson_data = load_geojson(file_path)

    # Define the point to check (longitude, latitude)
    point_to_check = (coords_3857)  # Replace with your desired coordinates

    # Find all features where the point is inside the polygon
    results = find_features_containing_point(geojson_data, point_to_check)

    if results:
        print(f"The point {point_to_check} is inside the following polygons:")
        for nuts_id, levl_code in results:
            #se il punto è dentro stampo il relativo codice del NUTS e livello
            print(f"- NUTS_ID: {nuts_id}, LEVL_CODE: {levl_code}")
    else:
        print(f"The point {point_to_check} is not inside any polygon.")

if __name__ == "__main__":
    main()


