BlynkLib
========

This package contains a single file to interface with the Blynk cloud  

To install
----------

Currently there is no pip install.  It is just a single file

Attribution
-----------

This library was inspired by, and leveraged from, the work of the WIPY project.

https://github.com/wipy/wipy/blob/master/lib/blynk/BlynkLib.py

Overview
--------

This BlynkLib is a hardware independent implementation of a BlynkLib interface.

This library requires developer implemented callbacks for all of the digital, analog and virtual pins, that are defined in the Blynk project.

The benefit of this is that someone can use this on any controller that has a python implementation.  For example, Raspberry PI, Onion Omega, Respeaker.  The developer just has to implement the necessary callbacks to interface with their hardware platform.

Creating an instance
--------------------

```python
import BlynkLib
auth_token='your token here'
blynk = BlynkLib.Blynk(auth_token)
```

At this point an instance is created, but it has **not** tried to connect to the Blynk cloud.
 

Digital Read Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to read a value from the controller.

The digital read callback is defined like:

```python
def digital_read_callback(pin, state, blynk_ref):
    digital_value = 0       # access your hardware
    return digital_value
    
```
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Digital Read Callback
------------------------------

To register the callback:

```python
blynk.add_digital_hw_pin(pin=pin_number, read=digital_read_callback, inital_state=None)
```
* pin: pin to associate the callback with
* read: read callback reference
* initial_state: dictionary of any initial state to pass with the callback.


Digital Write Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to write a value to the controller.

The digital write callback is defined like:

```python
def digital_write_callback(value, pin, state, blynk_ref):
    # access the neccessary digital output and write the value
    return
```
* value: digital value from the Blynk App
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Digital write Callback
------------------------------

To register the callback:

```python
blynk.add_digital_hw_pin(pin=pin_number, write=digital_write_callback, inital_state=None)
```
* pin: pin to associate the callback with
* write: write callback reference
* initial_state: dictionary of any initial state to pass with the callback.



Analog Read Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to read a value from the controller.

The analog read callback is defined like:

```python
def analog_read_callback(pin, state, blynk_ref):
    analog_value = 3.14159       # access your hardware
    return analog_value
    
```
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Analog Read Callback
------------------------------

To register the callback:

```python
blynk.add_analog_hw_pin(pin=pin_number, read=analog_read_callback, inital_state=None)
```
* pin: pin to associate the callback with
* read: read callback reference
* initial_state: dictionary of any initial state to pass with the callback.


Analog Write Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to write a value to the controller.

The analog write callback is defined like:

```python
def analog_write_callback(value, pin, state, blynk_ref):
    # access the neccessary analog output and write the value
    return
```
* value: analog value from the Blynk App
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Analog write Callback
------------------------------

To register the callback:

```python
blynk.add_analog_hw_pin(pin=pin_number, write=analog_write_callback, inital_state=None)
```
* pin: pin to associate the callback with
* write: write callback reference
* initial_state: dictionary of any initial state to pass with the callback.


Virtual Pin Read Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to read a value from the controller on a virtual pin.

The virtual pin read callback is defined like:

```python
def virtual_read_callback(pin, state, blynk_ref):
    virtual_value = 'Anything'       # access your hardware
    return virtual_value
    
```
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Virtual Pin Read Callback
------------------------------

To register the callback:

```python
blynk.add_virtual_pin(pin=pin_number, read=virtual_read_callback, inital_state=None)
```
* pin: pin to associate the callback with
* read: read callback reference
* initial_state: dictionary of any initial state to pass with the callback.


Virtual Pin Write Callback
----------------------

This happens when a widgit is defined in the Blynk app that would like to write a value to the controller.

The virtual pin write callback is defined like:

```python
def virtual_write_callback(value, pin, state, blynk_ref):
    # access the neccessary virtual output and write the value
    return
```
* value: value from the Blynk App
* pin: the pin number to associate with the call back.  If you have a one to one mapping between the pin and the callback, then the implementation of the callback generally knows the pin it should access.  But if you would like to create a single callback, and use the pin parameter to distinguish which pin to read, then the pin value is available.
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register Virtual Pin write Callback
------------------------------

To register the callback:

```python
blynk.add_virtual_pin(pin=pin_number, write=virtual_write_callback, inital_state=None)
```
* pin: pin to associate the callback with
* write: write callback reference
* initial_state: dictionary of any initial state to pass with the callback.


User Tasks
----------

It is also possible to setup periodic user tasks.  These tasks will be called based on the period specified instead of any particular Blynk Application interaction.

User Task Callback
------------------

```python
def user_task_callback(state, blynk_ref):
    # do anything you like, update the state, access the blynk referece
    return
```
* state: dictionary associated with the callback and provides the callback with a way to associate state between calls.  
* blynk_ref: reference to the blynk instance.  Generally not needed, but made available

Register User Task
------------------

```python
blynk.add_user_task(task=user_task_callback, second_period=2, initial_state=None)
```
* task: callback of the user task
* second_period: number of seconds between calls to the user task
* initial_state: dictionary of any initial state to pass with the callback.


Sample Applications
------------------

There are sample test applications:

### GenericBlynkTest.py
This test uses the Blynk Generic board and accesses an analog read

### OmegaBlynkType.py
This test uses the Onion Omega board and accesses a number of the interfaces.


Changes
-------

### June 24 2017
* change the run method to include a try/catch if any exception happens
in the run method.  If an exception occurs, this client will sleep 2 
seconds and try the run method again.  The goal is to not unexpectedly
exit the run method.

### June 5 2017
* Added authenticated flag to UserTask. 
True - user task can only run if the application is authenticated with Blynk server
False - user task can run without being authenticated.  Useful for background
      activities

### May 2017
* Added NoValueToReport exception.  If a read handler has no value to report back, 
then throwing a NoValueToReport exception will cause BlynkLib to just ignore it.

      
