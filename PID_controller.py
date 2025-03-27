import matplotlib.pyplot as plt
class controller :
    def __init__(self, name, debug_mode = True, k_p = 1, k_i = 0.1 ,k_d = 0.1):
        self.debug_mode = debug_mode
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.error = 0
        self.error_prev = 0
        self.integral = 0
    def calculate(self, setpoint, measurement):
        if self.debug_mode:
            #do graph thingid  with these 3 setpoint output measurement
        self.error = setpoint - measurement
        self.integral += self.error
        derivative = self.error - self.error_prev
        self.error_prev = self.error
        output = self.k_p * self.error + self.k_i * self.integral + self.k_d * derivative

        return output

# write test code for this lib like if __name__
if __name__ == "__main__":
    # create an instance of the controller
    controller = controller("test", debug_mode = True, k_p = 1, k_i = 0.1, k_d = 0.1)
    # set the setpoint and measurement

    setpoint = 10
    measurement = 5
    # add graph to this
    for i 
