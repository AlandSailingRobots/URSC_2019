import smbus

bus = smbus.SMBus(1)

t = bus.read_byte_data(0x60, 0x1E)
print(int(t))
