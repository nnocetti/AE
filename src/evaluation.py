import requests
from requests.exceptions import ConnectionError

OSRM_HOST = 'localhost:5000'
session = requests.Session()

class Evaluation:
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets

    def evaluate(self, ind, *, show=False):
        travel_max = 0
        query = ['' for _ in range(len(self.sources))]
        query_order = [[] for _ in range(len(self.sources))]
        deliver_time = [None for _ in range(len(self.targets))]

        # Construyo las urls para realizar las consultas
        # tengo que guardar el orden en que se recorren los destinos para cada origen, para poder calcular el tiempo de entrega a cada destino
        # recorro la codificacion del individuo
        for src, tgt in zip(ind[0], ind[1]):
            query[src] += f";{self.targets[tgt][1]},{self.targets[tgt][2]}"
            query_order[src].append(tgt)
        # para cada origen
        for i in range(len(self.sources)):
            # Si hay algun envio desde ese origen armo la url, consulto y proceso la respuesta
            if query[i]:
                query[i] = f"http://{OSRM_HOST}/route/v1/driving/{self.sources[i][0]},{self.sources[i][1]}{query[i]}"
                if show:
                    print(query[i])

                for j in range(3):
                    try:
                        data = session.get(query[i]).json()
                    except ConnectionError as error:
                        if j < 2:
                            continue
                        raise error
                    else:
                        break

                # Calculo la duracion del recorrido
                if show:
                    print('target travel_partial travel_and_delivery accumulated initial_wait deliver_time')
                travel_time = 0
                for j, durations in enumerate(data['routes'][0]['legs']):
                    travel_partial = durations['duration']
                    travel_and_delivery = travel_partial + 180
                    travel_time += travel_and_delivery
                    # Guardo el tiempo de llegada al destino sumando el tiempo desde que se realizo el pedidio y la duracion del viaje
                    initial_wait = self.targets[query_order[i][j]][0]
                    deliver_time[query_order[i][j]] = initial_wait + travel_time
                    if show:
                        print(f'{query_order[i][j]: <7}{travel_partial: <15.1f}{travel_and_delivery: <20.1f}{travel_time: <12.1f}{initial_wait: <13}{deliver_time[query_order[i][j]]: <8.1f}')

                # Me quedo con la duracion maxima
                if travel_time > travel_max:
                    travel_max = travel_time

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        if show:
            print(f'deliver_mean: {deliver_mean}')
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return travel_max, deliver_aad
