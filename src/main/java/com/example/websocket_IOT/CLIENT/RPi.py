try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    print("GPIO module not available, running in simulation mode.")
    from unittest import mock
    GPIO = mock.Mock()
