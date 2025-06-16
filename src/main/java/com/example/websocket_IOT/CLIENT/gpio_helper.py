# gpio_helper.py

try:
    import RPi.GPIO as _GPIO
    gpio_available = True
except (ImportError, RuntimeError):
    print("[INFO] GPIO module not available. Running in simulation mode.")
    gpio_available = False

if gpio_available:
    class GPIO:
        BCM = _GPIO.BCM
        OUT = _GPIO.OUT
        IN = _GPIO.IN

        def setmode(self, mode): _GPIO.setmode(mode)
        def setup(self, pin, mode): _GPIO.setup(pin, mode)
        def output(self, pin, state): _GPIO.output(pin, state)
        def input(self, pin): return _GPIO.input(pin)
        def cleanup(self): _GPIO.cleanup()
else:
    class GPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"

        def setmode(self, mode):
            print(f"[SIM] setmode({mode})")

        def setup(self, pin, mode):
            print(f"[SIM] setup(pin={pin}, mode={mode})")

        def output(self, pin, state):
            print(f"[SIM] output(pin={pin}, state={state})")

        def input(self, pin):
            print(f"[SIM] input(pin={pin}) => False")
            return False

        def cleanup(self):
            print("[SIM] cleanup()")
