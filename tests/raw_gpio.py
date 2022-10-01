import pigpio

sck_pin = 1
dout_pin = 2
channel_select = 'A'
channel_A_gain = 128

pi = pigpio.pi()

# init GPIO
pi.set_mode(sck_pin, pigpio.OUTPUT)  # sck_pin is output only
pi.set_mode(dout_pin, pigpio.INPUT)  # dout_pin is input only

# prepare for read
pi.write(sck_pin, 0)  # start by setting the pd_sck to 0
# check if dout pin is ready by confirming zero
for _ in range(20):
    ready = (pi.read(dout_pin) == 0)
    if ready:
        break

if not ready:
    print('GPIO pin not ready, quitting..')
    quit()

# for each bit in 24 bits, perform ADC read
raw_read = 0
for _ in range(24):
    # pulse sck high to request each bit
    pi.gpio_trigger(sck_pin,1,1)
    # left shift by one bit then bitwise OR with the new bit
    raw_read = (raw_read << 1) | pi.read(dout_pin)

# set channel after read
# get number of pulses based on channel configuration
num_pulses = 2  # default 2 for channel B
if channel_select == 'A' and channel_A_gain == 128:
    num_pulses = 1
elif channel_select == 'A' and channel_A_gain == 64:
    num_pulses = 3
# pulse num_pulses
for _ in range(num_pulses):
    pi.gpio_trigger(sck_pin,1,1)

print(f'Raw read (2s complement): {raw_read}')
if raw_read in [0x800000, 0x7FFFFF, 0xFFFFFF]:
    print(f'Invalid raw value detected')
# calculate int from 2's complement
# check if the sign bit is 1, indicating a negative number
if (raw_read & 0x800000):
    # convert from 2's complement to negative int
    signed_value = -((raw_read ^ 0xffffff) + 1)
else:  # else do not do anything the value is positive number
    signed_value = raw_read
print(f'Raw read (signed integer): {signed_value}')

pi.stop()