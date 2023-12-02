### Instalación OSRM

https://github.com/Project-OSRM/osrm-backend

Docker

https://hub.docker.com/r/osrm/osrm-backend/

Mapa Uruguay

https://download.geofabrik.de/south-america/uruguay.html


Resumen (PowerShell)

    # Descargamos mapa
    wget -O uruguay.osm.pbf https://download.geofabrik.de/south-america/uruguay-latest.osm.pbf
    # Creamos container "osrm", volumen "osrm-volumen" y copiamos mapa (no ejecutamos el container porque antes hay que preprocesar el mapa)
    docker create --name osrm -p 5000:5000 -v osrm-volume:/data osrm/osrm-backend osrm-routed --algorithm mld /data/uruguay.osrm
    docker cp uruguay.osm.pbf osrm:/data
    # Pre-process
    docker run --rm -t -v osrm-volume:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/uruguay.osm.pbf
    docker run --rm -t -v osrm-volume:/data osrm/osrm-backend osrm-partition /data/uruguay.osm.pbf
    docker run --rm -t -v osrm-volume:/data osrm/osrm-backend osrm-customize /data/uruguay.osrm
    # Primer inicio (-a) <- opcional
    docker start osrm -a

NOTA!

El paquete python pfevaluator tiene como requerimiento el paquete pygmo, que requiere un binario. Para poder instalarlo con pip, sin compilar, es necesario instalar algunas herramientas de pip (solo funciona en linux!)
    $ python3 -m pip install --upgrade pip setuptools wheel
