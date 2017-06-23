# Python based Blynk library without specific hardware dependencies.
# This adaptation to the library mentioned below, removes any specific hardware
# dependencies and makes the interface to the Blynk cloud and application generic
#
# Changes:
# * Removed Micro Python WIPY dependencies
# * Works with Python 2 and 3
# * replaced prints with Logging.
# * add 'add_digital_hw_pin' method to add hardware callbacks in a platform agnostic way
# * add 'add_analog_hw_pin' method to add hardware callbacks in a platform agnostic way
# * add 'add_virtual_pin' method to add a hardware callback for virtual pints in a platform agnostic way
# * add 'add_user_task' method to add as many user tasks as desired.  Each user task runs in its own thread
# * remove 'set_user_task' method in favor of add_user_task
#
# Changes: 5/22/2017
# * add execption:  NoValueToReport exception.  this exception is thrown
#                   when the callback does not want a value sent to the
#                   blynk server
# Changes 6/10/2017
# * all user tasks to run without being authenticated with blynk server
# TODO
# * all for run to be async in the background


# original Example Text and License
# Micro Python library that brings out-of-the-box Blynk support to
# the WiPy. Requires a previously established internet connection
# and a valid token string.
#
# Example usage:
#
#     import BlynkLib
#     import time
#
#     blynk = BlynkLib.Blynk('08a46fbc7f57407995f576f3f84c3f72')
#
#     # define a virtual pin read handler
#     def v0_read_handler():
#         # we must call virtual write in order to send the value to the widget
#         blynk.virtual_write(0, time.ticks_ms() // 1000)
#
#     # register the virtual pin
#     blynk.add_virtual_pin(0, read=v0_read_handler)
#
#     # define a virtual pin write handler
#     def v1_write_handler(value):
#         print(value)
#
#     # register the virtual pin
#     blynk.add_virtual_pin(1, write=v1_write_handler)
#
#     # register the task running every 3 sec
#     # (period must be a multiple of 50 ms)
#     def my_user_task():
#         # do any non-blocking operations
#         print('Action')
#
#     blynk.set_user_task(my_user_task, 3000)
#
#     # start Blynk (this call should never return)
#     blynk.run()
#
# -----------------------------------------------------------------------------
#
# This file is part of the Micro Python project, http://micropython.org/
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Daniel Campora
# Copyright (c) 2015 Volodymyr Shymanskyy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import socket
import struct
import time
import threading

const = lambda x: x

HDR_LEN = const(5)
HDR_FMT = "!BHH"

MAX_MSG_PER_SEC = const(20)

MSG_RSP = const(0)
MSG_LOGIN = const(2)
MSG_PING = const(6)
MSG_TWEET = const(12)
MSG_EMAIL = const(13)
MSG_NOTIFY = const(14)
MSG_BRIDGE = const(15)
MSG_HW_SYNC = const(16)
MSG_HW_INFO = const(17)
MSG_HW = const(20)

STA_SUCCESS = const(200)

HB_PERIOD = const(10)
NON_BLK_SOCK = const(0)
MIN_SOCK_TO = const(1)  # 1 second
MAX_SOCK_TO = const(5)  # 5 seconds, must be < HB_PERIOD
WDT_TO = const(10000)  # 10 seconds
RECONNECT_DELAY = const(1)  # 1 second
TASK_PERIOD_RES = const(50)  # 50 ms
IDLE_TIME_MS = const(5)  # 5 ms

RE_TX_DELAY = const(2)
MAX_TX_RETRIES = const(3)

MAX_VIRTUAL_PINS = const(128)

DISCONNECTED = 0
CONNECTING = 1
AUTHENTICATING = 2
AUTHENTICATED = 3

EAGAIN = const(11)

class NoValueToReport(Exception):
    pass

def now_in_ms():
    millis = int(round(time.time() * 1000))
    return millis


def sleep_from_until(start, delay):
    now = now_in_ms()
    ms_delta = now - start
    while ms_delta < delay:
        time.sleep(delay - ms_delta)
        now = now_in_ms()
        ms_delta = now - start

    return start + delay


class VrPin:
    def __init__(self, read=None, write=None, blynk_ref=None, initial_state=None):
        self.read = read
        self.write = write
        self.state = initial_state if initial_state is not None else {}
        self.blynk_ref = blynk_ref


class HwPin:
    def __init__(self, read=None, write=None, blynk_ref=None, initial_state=None):
        self.read = read
        self.write = write
        self.state = initial_state if initial_state is not None else {}
        self.blynk_ref = blynk_ref


class UserTask:
    def __init__(self, task_handler, period_in_seconds, blynk_ref, initial_state=None, authenticated=True):
        self.task_handler = task_handler
        self.period_in_seconds = period_in_seconds if period_in_seconds > 0 else 1
        self.task_state = initial_state if initial_state is not None else {}
        self.blynk_ref = blynk_ref
        # True - then only run UserTask if we have authenticated the blynk app
        # False - run the user task regardless of authenticated status
        self.authenticated = authenticated

    def run_task(self):
        if self.task_handler and (self.authenticated == False or (self.authenticated == True and self.blynk_ref.state == AUTHENTICATED)):
            self.task_handler(self.task_state, self.blynk_ref)

        the_timer = threading.Timer(self.period_in_seconds, self.run_task)
        the_timer.daemon = True
        the_timer.start()


class Terminal:
    def __init__(self, blynk, pin):
        self._blynk = blynk
        self._pin = pin

    def write(self, data):
        self._blynk.virtual_write(self._pin, data)

    def read(self, size):
        return ''

    def virtual_read(self):
        pass

    def virtual_write(self, value):
        try:
            out = eval(value)
            if out != None:
                logging.getLogger().info(repr(out))
        except:
            try:
                exec (value)
            except Exception as e:
                logging.getLogger().error('Exception:\n  ' + repr(e))


class Blynk:
    def __init__(self, token, server='blynk-cloud.com', port=None, connect=True, ssl=False):
        self._vr_pins = {}
        self._do_connect = False
        self._on_connect = None
        self._token = token
        if isinstance(self._token, str):
            self._token = str.encode(token)
        self._server = server
        if port is None:
            if ssl:
                port = 8441
            else:
                port = 8442
        self._port = port
        self._do_connect = connect
        self._ssl = ssl
        self.state = DISCONNECTED
        self._digital_hw_pins = {}
        self._analog_hw_pins = {}
        self.user_tasks = []
        self.state = DISCONNECTED


    def _format_msg(self, msg_type, *args):
        data = bytes('\0'.join(map(str, args)))
        return struct.pack(HDR_FMT, msg_type, self._new_msg_id(), len(data)) + data

    def _handle_hw(self, data):
        params = list(map(lambda x: x.decode('ascii'), data.split(b'\0')))
        cmd = params.pop(0)
        logging.getLogger().debug("command: {}".format(cmd))
        if cmd == 'info':
            pass
        elif cmd == 'pm':
            pairs = zip(params[0::2], params[1::2])
            for (pin, mode) in pairs:
                pin = int(pin)
                if mode != 'in' and mode != 'out' and mode != 'pu' and mode != 'pd':
                    raise ValueError("Unknown pin %d mode: %s" % (pin, mode))
                logging.getLogger().debug("pm: pin: {}, mode: {}".format(pin, mode))
            self._pins_configured = True
        elif cmd == 'vw':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].write:
                for param in params:
                    self._vr_pins[pin].write(param, pin, self._vr_pins[pin].state, self._vr_pins[pin].blynk_ref)
            else:
                logging.getLogger().warn("Warning: Virtual write to unregistered pin %d" % pin)
        elif cmd == 'vr':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].read:
                try:
                    val = self._vr_pins[pin].read(pin, self._vr_pins[pin].state, self._vr_pins[pin].blynk_ref)
                    self.virtual_write(pin, val)
                except NoValueToReport as nvtr:
                    pass
                except Exception as exc:
                    logging.getLogger().error("Exception in read handler: {}".format(exc))

            else:
                logging.getLogger().warn("Warning: Virtual read from unregistered pin %d" % pin)
        elif self._pins_configured:
            if cmd == 'dw':
                pin = int(params.pop(0))
                val = int(params.pop(0))
                if pin in self._digital_hw_pins:
                    if self._digital_hw_pins[pin].write is not None:
                        self._digital_hw_pins[pin].write(val, pin, self._digital_hw_pins[pin].state, self._digital_hw_pins[pin].blynk_ref)
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no digital 'write' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for digital write".format(pin))

            elif cmd == 'aw':
                pin = int(params.pop(0))
                val = int(params.pop(0))
                if pin in self._analog_hw_pins:
                    if self._analog_hw_pins[pin].write is not None:
                        self._analog_hw_pins[pin].write(val, pin, self._analog_hw_pins[pin].state, self._analog_hw_pins[pin].blynk_ref)
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no analog 'write' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for analog write".format(pin))

            elif cmd == 'dr':
                pin = int(params.pop(0))
                if pin in self._digital_hw_pins:
                    if self._digital_hw_pins[pin].read is not None:
                        try:
                            val = self._digital_hw_pins[pin].read(pin, self._digital_hw_pins[pin].state, self._digital_hw_pins[pin].blynk_ref)
                            self._send(self._format_msg(MSG_HW, 'dw', pin, val))
                        except NoValueToReport as nvtr:
                            pass
                        except Exception as exc:
                            logging.getLogger().error("Error in digital read handler: {}".format(exc))
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no digital 'read' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for digital read".format(pin))

            elif cmd == 'ar':
                pin = int(params.pop(0))
                if pin in self._analog_hw_pins:
                    if self._analog_hw_pins[pin].read is not None:
                        try:
                            val = self._analog_hw_pins[pin].read(pin, self._analog_hw_pins[pin].state, self._analog_hw_pins[pin].blynk_ref)
                            self._send(self._format_msg(MSG_HW, 'aw', pin, val))
                        except NoValueToReport as nvtr:
                            pass
                        except Exception as exc:
                            logging.getLogger().error("Error in analog read callback: {}".format(exc))
                    else:
                        logging.getLogger().warn("Warning: Hardware pin: {} is setup, but has no analog 'read' callback.".format(pin))
                else:
                    logging.getLogger().warn("Warning: Hardware pin: {} not setup for analog read".format(pin))
            else:
                raise ValueError("Unknown message cmd: %s" % cmd)

    def _new_msg_id(self):
        self._msg_id += 1
        if (self._msg_id > 0xFFFF):
            self._msg_id = 1
        return self._msg_id

    def _settimeout(self, timeout):
        if timeout != self._timeout:
            self._timeout = timeout
            self.conn.settimeout(timeout)

    def _recv(self, length, timeout=0):
        self._settimeout(timeout)
        try:
            self._rx_data += self.conn.recv(length)
        except socket.timeout:
            return b''
        except socket.error as e:
            if e.args[0] == EAGAIN:
                return b''
            else:
                raise
        if len(self._rx_data) >= length:
            data = self._rx_data[:length]
            self._rx_data = self._rx_data[length:]
            return data
        else:
            return b''

    def _send(self, data, send_anyway=False):
        if self._tx_count < MAX_MSG_PER_SEC or send_anyway:
            retries = 0
            while retries <= MAX_TX_RETRIES:
                try:
                    self.conn.send(data)
                    self._tx_count += 1
                    break
                except socket.error as er:
                    if er.args[0] != EAGAIN:
                        raise
                    else:
                        time.sleep_ms(RE_TX_DELAY)
                        retries += 1

    def _close(self, emsg=None):
        self.conn.close()
        self.state = DISCONNECTED
        time.sleep(RECONNECT_DELAY)
        if emsg:
            logging.getLogger().info('Error: %s, connection closed' % emsg)

    def _server_alive(self):
        c_time = int(time.time())
        if self._m_time != c_time:
            self._m_time = c_time
            self._tx_count = 0
            if self._last_hb_id != 0 and c_time - self._hb_time >= MAX_SOCK_TO:
                return False
            if c_time - self._hb_time >= HB_PERIOD and self.state == AUTHENTICATED:
                self._hb_time = c_time
                self._last_hb_id = self._new_msg_id()
                self._send(struct.pack(HDR_FMT, MSG_PING, self._last_hb_id, 0), True)
        return True

    def repl(self, pin):
        repl = Terminal(self, pin)
        self.add_virtual_pin(pin, repl.virtual_read, repl.virtual_write)
        return repl

    def notify(self, msg):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_NOTIFY, msg))

    def tweet(self, msg):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_TWEET, msg))

    def email(self, to, subject, body):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_EMAIL, to, subject, body))

    def virtual_write(self, pin, val):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW, 'vw', pin, val))

    def sync_all(self):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC))

    def sync_virtual(self, pin):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW_SYNC, 'vr', pin))

    def add_virtual_pin(self, pin, read=None, write=None, initial_state=None):
        if isinstance(pin, int) and pin in range(0, MAX_VIRTUAL_PINS):
            self._vr_pins[pin] = VrPin(read=read, write=write, blynk_ref=self, initial_state=initial_state)
        else:
            raise ValueError('the pin must be an integer between 0 and %d' % (MAX_VIRTUAL_PINS - 1))

    def add_digital_hw_pin(self, pin, read=None, write=None, inital_state=None):
        """
        add a callback for a hw defined pin for digital input/output.
        :param pin: pin number
        :param read: called when a value should be read from the hardware.
                     Depending upon how it is setup in the blynk app, will depend
                     upon whether this is reading a digital or analog value
        :param write: called when a value should be written to the hardware.
                        Depending upon how it is setup in the blynk app, will determine
                        if this is wring a digital or analog value.

        :return: None
        """
        if isinstance(pin, int):
            self._digital_hw_pins[pin] = HwPin(read=read, write=write, blynk_ref=self, initial_state=inital_state)
        else:
            raise ValueError("pin value must be an integer value")

    def add_analog_hw_pin(self, pin, read=None, write=None, initial_state=None):
        """
        add a callback for a hw defined pin for analog input/output.
        :param pin: pin number
        :param read: called when a value should be read from the hardware.
                     Depending upon how it is setup in the blynk app, will depend
                     upon whether this is reading a digital or analog value
        :param write: called when a value should be written to the hardware.
                        Depending upon how it is setup in the blynk app, will determine
                        if this is wring a digital or analog value.

        :return: None
        """
        if isinstance(pin, int):
            self._analog_hw_pins[pin] = HwPin(read=read, write=write, blynk_ref=self, initial_state=initial_state)
        else:
            raise ValueError("pin value must be an integer value")


    def on_connect(self, func):
        self._on_connect = func

    def add_user_task(self, task, second_period, initial_state=None, authenticated=True):
        """
        Add a user defined task to be called every 'second_period' seconds.
        Each user task runs in its own thread and it is up to the tasks
        to synchronize any threads if necessary.

        :param task: callback function of the form: user_task(task_state, blynk_ref)
        :param second_period: number of seconds between calls
        :param task_state: initial task state
        :param authenticated: True - wait for the application to be authenticated, before
                        allowing the user task to run.
                      False - allow the task to run regardless of authentication
        :return: None
        """
        self.user_tasks.append(UserTask(task, second_period, self, initial_state, authenticated))

    def connect(self):
        self._do_connect = True

    def disconnect(self):
        self._do_connect = False

    def run(self):
        """
        Run the Blynk client in a blocking mode, catching and eating
        exceptions.  Upon an exception, the Blynk client will sleep
        for 2 seconds and then call the internal _run method again.
        :return:
        """
        while True:
            try:
                self._run()
            except:
                time.sleep(2)

    def _run(self):
        """
        Run the Blynk client in a blocking mode
        :return:
        """
        self._start_time = now_in_ms()
        self._task_millis = self._start_time
        self._rx_data = b''
        self._msg_id = 1
        self._pins_configured = False
        self._timeout = None
        self._tx_count = 0
        self._m_time = 0

        # start all of the tasks, which will be blocked on the
        # state going to AUTHENTICATED
        for task in self.user_tasks:
            task.run_task()

        while True:
            while self.state != AUTHENTICATED:
                if self._do_connect:
                    try:
                        self.state = CONNECTING
                        if self._ssl:
                            import ssl
                            logging.getLogger().debug('SSL: Connecting to %s:%d' % (self._server, self._port))
                            ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SEC)
                            self.conn = ssl.wrap_socket(ss, cert_reqs=ssl.CERT_REQUIRED, ca_certs='/flash/cert/ca.pem')
                        else:
                            logging.getLogger().debug('TCP: Connecting to %s:%d' % (self._server, self._port))
                            self.conn = socket.socket()
                        self.conn.connect(socket.getaddrinfo(self._server, self._port)[0][4])
                    except:
                        self._close('connection with the Blynk servers failed')
                        continue

                    self.state = AUTHENTICATING
                    hdr = struct.pack(HDR_FMT, MSG_LOGIN, self._new_msg_id(), len(self._token))
                    logging.getLogger().debug('Blynk connection successful, authenticating...')
                    self._send(hdr + self._token, True)
                    data = self._recv(HDR_LEN, timeout=MAX_SOCK_TO)
                    if not data:
                        self._close('Blynk authentication timed out')
                        continue

                    msg_type, msg_id, status = struct.unpack(HDR_FMT, data)
                    if status != STA_SUCCESS or msg_id == 0:
                        self._close('Blynk authentication failed')
                        continue

                    self.state = AUTHENTICATED
                    self._send(self._format_msg(MSG_HW_INFO, "h-beat", HB_PERIOD, 'dev', 'WiPy', "cpu", "CC3200"))
                    logging.getLogger().debug('Access granted, happy Blynking!')
                    if self._on_connect:
                        self._on_connect()
                else:
                    self._start_time = sleep_from_until(self._start_time, TASK_PERIOD_RES)

            self._hb_time = 0
            self._last_hb_id = 0
            self._tx_count = 0
            while self._do_connect:
                data = self._recv(HDR_LEN, NON_BLK_SOCK)
                if data:
                    msg_type, msg_id, msg_len = struct.unpack(HDR_FMT, data)
                    if msg_id == 0:
                        self._close('invalid msg id %d' % msg_id)
                        break
                    if msg_type == MSG_RSP:
                        if msg_id == self._last_hb_id:
                            self._last_hb_id = 0
                    elif msg_type == MSG_PING:
                        self._send(struct.pack(HDR_FMT, MSG_RSP, msg_id, STA_SUCCESS), True)
                    elif msg_type == MSG_HW or msg_type == MSG_BRIDGE:
                        data = self._recv(msg_len, MIN_SOCK_TO)
                        if data:
                            self._handle_hw(data)
                    else:
                        self._close('unknown message type %d' % msg_type)
                        break
                else:
                    self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
                if not self._server_alive():
                    self._close('Blynk server is offline')
                    break


            if not self._do_connect:
                self._close()
                logging.getLogger().debug('Blynk disconnection requested by the user')
