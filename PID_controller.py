class controller :
    def __init__(self, name, debug_mode = True, k_p = 1, k_i = 0.1 ,k_d = 0.1):
        self.debug_mode = debug_mode
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.error = 0
        self.error_prev = 0
        self.integral = 0
        self.integral_prev = 0
    def calculate(self, setpoint, measurement):
        self.error = setpoint - measurement
        self.integral += self.error
        self.integral_prev = self.integral
        derivative = self.error - self.error_prev
        self.error_prev = self.error
        return self.k_p * self.error + self.k_i * self.integral + self.k_d * derivative
    