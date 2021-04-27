# Winch code with the use of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 for a duration, hold for a duration and then return .
# Author: Vidar Harding & Evelin Bergvall
from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min,  max and stall servo pulse lengths
servo_min = 340
servo_max = 450
servo_still = 390

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 60hz, good for servos.
pwm.se_pwm_freq(60)

print('Moving servo on channel 0, press Ctrl-C to quit...')
# Move servo clockwise  on channel O time_Z, hold time_H, then counter clockwise time_Z.
time_Z = 10

time_H = 20

pwm.set_pwm(0, 0, servo_min)
time.sleep(time_Z)
pwm.set_pwm(0, 0, servo_still)
time.sleep(time_H)            #Go to Ellen and Ek's sensor codes
pwm.set_pwm(0, 0, servo_max)
time.sleep(time_Z)
pwm.set_pwm(0, 0, servo_still)
