import requests
from requests.exceptions import ConnectionError

OSRM_HOST = 'localhost:5000'
session = requests.Session()

class Evaluation:
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets

    def evaluate(self, ind):
        duration_max = 0
        query = ['' for _ in range(len(self.sources))]
        query_order = [[] for _ in range(len(self.sources))]
        deliver_time = [None for _ in range(len(self.targets))]

        print(ind)

        # Construyo las urls para realizar las consultas
        # tengo que guardar el orden en que se recorren los destinos para cada origen, para poder calcular el tiempo de entrega a cada destino
        # recorro la codificacion del individuo
        for src, tgt in zip(ind[0], ind[1]):
            print(f'{src},{tgt}')
            query[src] += f";{self.targets[tgt][1]},{self.targets[tgt][2]}"
            query_order[src].append(tgt)
        # para cada origen
        for i in range(len(self.sources)):
            # Si hay algun envio desde ese origen armo la url, consulto y proceso la respuesta
            if query[i]:
                query[i] = f"http://{OSRM_HOST}/route/v1/driving/{self.sources[i][0]},{self.sources[i][1]}{query[i]}"
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
                duration = 0
                for j, partial_durations in enumerate(data['routes'][0]['legs']):
                    duration += partial_durations['duration'] + 180
                    # Guardo el tiempo de llegada al destino sumando el tiempo desde que se realizo el pedidio y la duracion del viaje
                    deliver_time[query_order[i][j]] = self.targets[query_order[i][j]][0] + duration
                    print(f'target: {query_order[i][j]}, deliver_time: {deliver_time[query_order[i][j]]}')

                # Me quedo con la duracion maxima
                if duration > duration_max:
                    duration_max = duration

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        print(f'deliver_mean: {deliver_mean}')
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return duration_max, deliver_aad
