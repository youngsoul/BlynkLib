import BlynkLib
import time
import logging
import random
import OmegaGPIOHelper

logging.basicConfig(level=logging.DEBUG)

gpio = OmegaGPIOHelper.OmegaGPIOHelper()


def user_task_handler_2(task_state, blynk_ref):
    logging.getLogger().debug("user_task_handler_2: {}".format(time.time()))
    logging.getLogger().debug("user_task_handler_2: Blynk State: {}".format(blynk_ref.state))
    pass


def v127_write_handler(value, pin, state, blynk_ref):
    logging.getLogger().debug("V127 Param: {}".format(value))
    pass


def v126_read_handler(pin, state, blynk_ref):
    value = get_random_digital_value()
    if 'last_value' not in state:
        state['last_value'] = -1
    state['last_value'] = value
    return value


def user_task_handler(task_state, blynk_ref):
    # logging.getLogger().debug("v33 read handler")

    # we must call virtual write in order to send the value to the widget
    if task_state['led_state']:
        task_state['led_state'] = 0
    else:
        task_state['led_state'] = 1

    blynk_ref.virtual_write(33, 255 * task_state['led_state'])


def hw0_write_handler(value, pin, state, blynk_ref):
    logging.getLogger().debug("HW0 write value: {}".format(value))
    gpio.setPin(0, value)


def hw26_read_handler(pin, state, blynk_ref):
    pin26 = gpio.getPin(pin)
    logging.getLogger().debug("hw26_read_handler: {}".format(pin26))
    return pin26


def hw1_read_handler(pin, state, blynk_ref):
    value = get_random_digital_value()
    return value


def get_random_digital_value():
    if random.randint(0, 100) <= 50:
        value = 0
    else:
        value = 1
    return value


auth_token = ''

blynk = BlynkLib.Blynk(auth_token)
blynk.add_user_task(user_task_handler, 2, {'led_state': 0})
blynk.add_user_task(user_task_handler_2, 2)
blynk.add_digital_hw_pin(0, write=hw0_write_handler)
blynk.add_digital_hw_pin(1, read=hw1_read_handler)
blynk.add_virtual_pin(127, write=v127_write_handler)
blynk.add_virtual_pin(126, read=v126_read_handler)
blynk.add_digital_hw_pin(26, read=hw26_read_handler)

logging.getLogger().info("Running...")
blynk.run()
