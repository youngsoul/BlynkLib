import BlynkLib
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG)


def analog_read_handler(pin, state, blynk_ref):
    value = get_random_analog_value()
    print("analog_read_handler[{}] = {}".format(pin, value))
    return value

def get_random_digital_value():
    value = None
    if random.randint(0, 100) <= 50:
        value = 0
    else:
        value = 1
    return value

def get_random_analog_value():
    value = random.random()*100

    return value

auth_token = ''

blynk = BlynkLib.Blynk(auth_token)
blynk.add_analog_hw_pin(1, read=analog_read_handler)

#blynk.add_virtual_pin(33, read=user_task_handler)
logging.getLogger().info("Running...")
blynk.run()
