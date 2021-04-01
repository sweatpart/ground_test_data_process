from collections import defaultdict

class DutyCycle():
    def __init__(self, series, config):
        self.series = iter(series)
        self.torque = config['main_parm']
        self.speed = config['optional_parms'][0]
        self.angal = config['optional_parms'][1]
        self.tire_radius = config['tire_radius']
        self.time_interval = config['time_interval']
    
    def extract_cycles(self):

        for line in self.series:
            count = float(line[self.speed]) * 1000 / 60 / (2 * 3.14 * self.tire_radius) * self.time_interval
            yield [float(line[self.torque]), count, float(abs(line[self.angal]))]
        
    def count_cycles(self):

        def _get_round_function(ndigits=None):
            if ndigits is None:
                return lambda x: x
            else:
                return lambda x: round(x, ndigits)
        
        result = defaultdict(dict)

        roundtorque_ = _get_round_function(-1)
        roundcount_ = _get_round_function(1)
        roundangal_ = _get_round_function(0)

        cycles = self.extract_cycles()
        round_cycles = ((roundtorque_(torque), roundcount_(count), roundangal_(angal)) for torque, count, angal in cycles)
        for torque, count, angal in round_cycles:
            try:
                result[torque][angal] += count
            except KeyError:
                result[torque][angal] = count
            #print(torque, count, angal)

        return result