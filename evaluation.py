import requests
from requests.exceptions import ConnectionError

OSRM_HOST = 'uckla.ddns.net:54321'


class Evaluation:
    def __init__(self, sources, targets, *, show = False):
        self.sources = sources
        self.targets = targets
        self.show = show
        self.session = requests.Session()


        # Construyo la url para obtener la tabla desde los origienes
        url = f'{self.sources[0][0]},{self.sources[0][1]}'
        for i in range(1, len(self.sources)):
            url += f';{self.sources[i][0]},{self.sources[i][1]}'
        for j in range(len(self.targets)):
            url += f';{self.targets[j][1]},{self.targets[j][2]}'
        url += '?sources=' + ';'.join(str(i) for i in range(len(self.sources)))
        url = f'http://{OSRM_HOST}/table/v1/driving/{url}'

        if self.show == True:
            print(url)
        for j in range(3):
            try:
                data = self.session.get(url).json()
                self.src2tgt = data['durations']
                for lst in self.src2tgt:
                    del lst[:3]
            except ConnectionError as error:
                if j < 2:
                    continue
                raise error
            else:
                break

        # Construyo la url para obtener la tabla entre los destinos
        url = f'{self.targets[0][1]},{self.targets[0][2]}'
        for i in range(1, len(self.targets)):
            url += f';{self.targets[i][1]},{self.targets[i][2]}'
        url = f'http://{OSRM_HOST}/table/v1/driving/{url}'

        if self.show == True:
            print(url)
        for j in range(3):
            try:
                self.tgt2tgt = self.session.get(url).json()['durations']
            except ConnectionError as error:
                if j < 2:
                    continue
                raise error
            else:
                break


    def evaluate(self, ind):
        travel_state = [None] * len(self.sources)
        travel_time = [0] * len(self.sources)
        deliver_time = [None] * len(self.targets)

        if self.show:
            print('source target travel_partial travel_and_delivery accumulated initial_wait deliver_time')

        for src, tgt in zip(ind[0], ind[1]):
            if travel_state[src] is None:
                travel_partial = self.src2tgt[src][tgt]
            else:
                travel_partial = self.tgt2tgt[travel_state[src]][tgt]
            travel_and_delivery = travel_partial + 180
            travel_time[src] += travel_and_delivery
            travel_state[src] = tgt
            initial_wait = self.targets[tgt][0]
            deliver_time[tgt] = initial_wait + travel_time[src]
            if self.show:
                print(f'{src: <7}{tgt: <7}{travel_partial: <15.1f}{travel_and_delivery: <20.1f}{travel_time[src]: <12.1f}{initial_wait: <13}{deliver_time[tgt]: <8.1f}')

        # Me quedo con la duracion maxima
        travel_max = max(travel_time)

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        if self.show:
            print(f'deliver_mean: {deliver_mean}')
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return travel_max, deliver_aad


    def evaluate_alternative(self, ind):
        travel_max = 0
        query = [''] * len(self.sources)
        query_order = [[] for _ in range(len(self.sources))]
        deliver_time = [None] * len(self.targets)

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
                if self.show:
                    print(query[i])

                for j in range(3):
                    try:
                        data = self.session.get(query[i]).json()
                    except ConnectionError as error:
                        if j < 2:
                            continue
                        raise error
                    else:
                        break

                # Calculo la duracion del recorrido
                if self.show:
                    print('target travel_partial travel_and_delivery accumulated initial_wait deliver_time')
                travel_time = 0
                for j, durations in enumerate(data['routes'][0]['legs']):
                    travel_partial = durations['duration']
                    travel_and_delivery = travel_partial + 180
                    travel_time += travel_and_delivery
                    # Guardo el tiempo de llegada al destino sumando el tiempo desde que se realizo el pedidio y la duracion del viaje
                    initial_wait = self.targets[query_order[i][j]][0]
                    deliver_time[query_order[i][j]] = initial_wait + travel_time
                    if self.show:
                        print(f'{query_order[i][j]: <7}{travel_partial: <15.1f}{travel_and_delivery: <20.1f}{travel_time: <12.1f}{initial_wait: <13}{deliver_time[query_order[i][j]]: <8.1f}')

                # Me quedo con la duracion maxima
                if travel_time > travel_max:
                    travel_max = travel_time

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        if self.show:
            print(f'deliver_mean: {deliver_mean}')
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return travel_max, deliver_aad