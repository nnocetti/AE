import requests
from requests.exceptions import ConnectionError

OSRM_HOST = 'localhost:5000'
session = requests.Session()

class Evaluation:
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets

        # Construyo la url para obtener la tabla desde los origienes
        url = f'{self.sources[0][0]},{self.sources[0][1]}'
        for i in range(1, len(self.sources)):
            url += f';{self.sources[i][0]},{self.sources[i][1]}'
        for j in range(len(self.targets)):
            url += f';{self.targets[j][1]},{self.targets[j][2]}'
        url += '?sources=' + ';'.join(str(i) for i in range(len(self.sources)))
        url = f'http://{OSRM_HOST}/table/v1/driving/{url}'

        for j in range(3):
            try:
                data = session.get(url).json()
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

        for j in range(3):
            try:
                self.tgt2tgt = session.get(url).json()['durations']
            except ConnectionError as error:
                if j < 2:
                    continue
                raise error
            else:
                break


    def evaluate(self, ind, *, show=False):
        travel_state = [None] * len(self.sources)        
        travel_time = [0] * len(self.sources)
        deliver_time = [None] * len(self.targets)

        if show:
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
            if show:
                print(f'{src: <7}{tgt: <7}{travel_partial: <15.1f}{travel_and_delivery: <20.1f}{travel_time[src]: <12.1f}{initial_wait: <13}{deliver_time[tgt]: <8.1f}')

        # Me quedo con la duracion maxima
        travel_max = max(travel_time)

        # Calculamos la desviación absoluta promedio (Average absolute deviation)
        deliver_mean = sum(deliver_time)/len(deliver_time)
        if show:
            print(f'deliver_mean: {deliver_mean}')
        deliver_aad = sum([abs(dtime-deliver_mean) for dtime in deliver_time])/len(deliver_time)

        return travel_max, deliver_aad
