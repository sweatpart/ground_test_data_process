from collections import defaultdict

class DutyCycle():
    def __init__(self, series, torque='torque', speed='speed', angal='angal', tire_radius=0.33, time_interval=0.05):
        self.series = iter(series)
        self.torque = torque
        self.speed = speed
        self.angal = angal
        self.tire_radius = tire_radius
        self.time_interval = time_interval
    
    def extract_cycles(self):

        for line in self.series:
            count = float(line[self.speed]) * 1000 / 60 / (2 * 3.14 * self.tire_radius) * self.time_interval
            yield [line[self.torque], count, line[self.angal]]
        
    def count_cycles(self):
        
        result = defaultdict(dict)

        cycles = self.extract_cycles()
        for torque, count, angal in cycles:
            try:
                result[torque][angal] += count
            except KeyError:
                result[torque][angal] = count
            print(torque, count, angal)

        return result