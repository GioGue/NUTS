
import json
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from pyproj import Transformer
import requests

#FUNCTIONS

def address_to_coordinates_4326(address):
    """Converti un indirizzo in coordinate con Nominatim."""
    print(address)
    #cerca subito indirizzo con OSM
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': address, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'NUTS/2.0 (your_email@example.com)'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        lon, lat = float(response.json()[0]['lon']), float(response.json()[0]['lat'])
        return lon, lat
    parts = address.split(", ")
    while len(parts) > 1:
        parts.pop(0)  # Elimina la prima parte dell'indirizzo
        new_address = ", ".join(parts)
        print(f"Tentativo con indirizzo semplificato: {new_address}")
        params = {'q': new_address, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'NUTS/2.0 (your_email@example.com)'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and response.json():
            lon, lat = float(response.json()[0]['lon']), float(response.json()[0]['lat'])
            return lon, lat

    else:
        raise ValueError("Indirizzo non trovato o errore di connessione.")


def transform_coordinates_4326_to_3857(coords_4326):
    """Transform coordinates from EPSG:4326 to EPSG:3857."""
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    return transformer.transform(*coords_4326)

def load_multipolygons_from_geojson(file_path):
    """Load MultiPolygons from a GeoJSON file and store related NUTS metadata."""
    multipolygons = []

    with open(file_path, 'r', encoding='utf-8') as file:
        geojson_data = json.load(file)

    if geojson_data.get('type') == 'FeatureCollection':
        for feature in geojson_data.get('features', []):
            geometry = feature.get('geometry')
            properties = feature.get('properties', {})

            if geometry is None:
                continue  # Skippa le geometrie non valide

            try:
                geom = shape(geometry)  # Converte GeoJSON in Shapely
                if isinstance(geom, (MultiPolygon, Polygon)):
                    multipolygons.append((MultiPolygon([geom]) if isinstance(geom, Polygon) else geom, properties))
            except Exception as e:
                print(f"Errore nella geometria: {e}")

    return multipolygons

def check_point_in_multipolygon(multipolygons, point_3857):
    """Check if a point is inside any MultiPolygon and print NUTS details."""
    point = Point(point_3857)
    found = False

    for mpoly, properties in multipolygons:
        if mpoly.contains(point):
            nuts_id = properties.get("NUTS_ID", "Unknown")
            levl_code = properties.get("LEVL_CODE", "Unknown")
            print(f"- NUTS_ID: {nuts_id}, LEVL_CODE: {levl_code}")
            found = True

    return found


#PROGRAMMA

def main():
    print("Avvio Programma")
    #sostituire il PATH dei file con quello corretto
    geojson_file_0 = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS_RG_01M_2024_3857_LEVL_0.geojson"  # Sostituisci con il percorso reale del file GeoJSON
    geojson_file_1 = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS_RG_01M_2024_3857_LEVL_1.geojson"
    geojson_file_2 = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS_RG_01M_2024_3857_LEVL_2.geojson"
    geojson_file_3 = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS_RG_01M_2024_3857_LEVL_3.geojson"
    #PATH dei file 2021 per includere NUTS UK
    geojson_file_0_UK = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS2021\NUTS_RG_01M_2021_3857_LEVL_0.geojson"  # Sostituisci con il percorso reale del file GeoJSON
    geojson_file_1_UK = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS2021\NUTS_RG_01M_2021_3857_LEVL_1.geojson"
    geojson_file_2_UK = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS2021\NUTS_RG_01M_2021_3857_LEVL_2.geojson"
    geojson_file_3_UK = r"C:\Users\giorg\Desktop\Politecnico\Tesi\programma\NUTS2021\NUTS_RG_01M_2021_3857_LEVL_3.geojson"

    while True:
        address = input("Inserisci l'indirizzo (o 'END per terminare'): ").strip()
        if address.upper() == "END":
            print("Chiusura del programma...")
            break
        try:
            # Converti l'indirizzo in coordinate e trasforma in EPSG:3857
            coords_4326 = address_to_coordinates_4326(address)
            coords_3857 = transform_coordinates_4326_to_3857(coords_4326)

            # NUTS 0: Carica i MultiPolygons e verifica se il punto è contenuto in essi
            multipolygons_0 = load_multipolygons_from_geojson(geojson_file_0)
            #if not multipolygons_0: #check valid multipolygons
            #    raise ValueError("No valid MultiPolygons found in the GeoJSON file.")
            is_inside = check_point_in_multipolygon(multipolygons_0, coords_3857)
            if not is_inside:
                #UK check
                multipolygons_0_UK= load_multipolygons_from_geojson(geojson_file_0_UK)
                is_inside_uk = check_point_in_multipolygon(multipolygons_0_UK, coords_3857)
                if not is_inside_uk:
                    print("Il punto non si trova in nessun NUTS_0.")

            # NUTS 1: Carica i MultiPolygons e verifica se il punto è contenuto in essi
            multipolygons_1 = load_multipolygons_from_geojson(geojson_file_1)
            is_inside = check_point_in_multipolygon(multipolygons_1, coords_3857)
            if not is_inside:
                 #UK check
                multipolygons_1_UK= load_multipolygons_from_geojson(geojson_file_1_UK)
                is_inside_uk = check_point_in_multipolygon(multipolygons_1_UK, coords_3857)
                if not is_inside_uk:
                    print("Il punto non si trova in nessun NUTS_1.")

            # NUTS 2: Carica i MultiPolygons e verifica se il punto è contenuto in essi
            multipolygons_2 = load_multipolygons_from_geojson(geojson_file_2)
            is_inside = check_point_in_multipolygon(multipolygons_2, coords_3857)
            if not is_inside:
                 #UK check
                multipolygons_2_UK= load_multipolygons_from_geojson(geojson_file_2_UK)
                is_inside_uk = check_point_in_multipolygon(multipolygons_2_UK, coords_3857)
                if not is_inside_uk:
                    print("Il punto non si trova in nessun NUTS_2.")

             # NUTS 3: Carica i MultiPolygons e verifica se il punto è contenuto in essi
            multipolygons_3 = load_multipolygons_from_geojson(geojson_file_3)
            is_inside = check_point_in_multipolygon(multipolygons_3, coords_3857)
            if not is_inside:
                #UK check
                multipolygons_3_UK= load_multipolygons_from_geojson(geojson_file_3_UK)
                is_inside_uk = check_point_in_multipolygon(multipolygons_3_UK, coords_3857)
                if not is_inside_uk:
                    print("Il punto non si trova in nessun NUTS_3.")

        except Exception as e:
            print(f"Errore: {e}")

if __name__ == "__main__":
    main()

#LA VERSIONE DEL PROGRAMMA FUNZIONA ANCHE CON QUESTI INDIRIZZI CHE DAVANO PROBLEMI CON LA VERSIONE 1.0:
#indirizzo attica: Ηρώων Πολυτεχνείου, Βρυώνη, 2nd District of Piraeus, Pireo, Municipality of Piraeus, Regional Unit of Piraeus, Attica, 185 36, Grecia
#indirizzo Bucarest doppio risultato: Bulevardul Ficusului 44A, București 013975, Romania
#indirizzo UK non trovato in 2024: Waterton Industrial Estate, Bridgend CF31 3WT, Regno Unito

#indirizzi non trovati:
#Viborg, West Julland, Danimarca ##non funzionante
