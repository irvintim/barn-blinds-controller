# VSP-WSC-4 Window Shade Controller
# Berry driver for H-bridge motor control via TB6612FNG

import gpio

# GPIO pin definitions
var PIN_STBY   = 37
var PIN_S1_OPN = 43
var PIN_S1_CLS = 2
var PIN_S2_OPN = 44
var PIN_S2_CLS = 42
var PIN_S3_OPN = 36
var PIN_S3_CLS = 35
var PIN_S4_OPN = 38
var PIN_S4_CLS = 39

# Initialize all pins as outputs, set low
var motor_pins = [PIN_S1_OPN, PIN_S1_CLS, PIN_S2_OPN, PIN_S2_CLS,
                  PIN_S3_OPN, PIN_S3_CLS, PIN_S4_OPN, PIN_S4_CLS, PIN_STBY]

for pin : motor_pins
    gpio.pin_mode(pin, gpio.OUTPUT)
    gpio.digital_write(pin, 0)
end

# Enable STBY permanently
gpio.digital_write(PIN_STBY, 1)

def update_motors()
    var power = tasmota.get_power()
    var n = size(power)

    # Shade 1: POWER1=open, POWER2=close
    var s1_open  = (n > 0) ? power[0] : false
    var s1_close = (n > 1) ? power[1] : false
    gpio.digital_write(PIN_S1_OPN, s1_open  ? 1 : 0)
    gpio.digital_write(PIN_S1_CLS, s1_close ? 1 : 0)

    # Shade 2: POWER3=open, POWER4=close
    var s2_open  = (n > 2) ? power[2] : false
    var s2_close = (n > 3) ? power[3] : false
    gpio.digital_write(PIN_S2_OPN, s2_open  ? 1 : 0)
    gpio.digital_write(PIN_S2_CLS, s2_close ? 1 : 0)

    # Shade 3: POWER5=open, POWER6=close
    var s3_open  = (n > 4) ? power[4] : false
    var s3_close = (n > 5) ? power[5] : false
    gpio.digital_write(PIN_S3_OPN, s3_open  ? 1 : 0)
    gpio.digital_write(PIN_S3_CLS, s3_close ? 1 : 0)

    # Shade 4: POWER7=open, POWER8=close
    var s4_open  = (n > 6) ? power[6] : false
    var s4_close = (n > 7) ? power[7] : false
    gpio.digital_write(PIN_S4_OPN, s4_open  ? 1 : 0)
    gpio.digital_write(PIN_S4_CLS, s4_close ? 1 : 0)
end

# Trigger on any power change
tasmota.add_rule("Power1#State", def(value) update_motors() end)
tasmota.add_rule("Power2#State", def(value) update_motors() end)
tasmota.add_rule("Power3#State", def(value) update_motors() end)
tasmota.add_rule("Power4#State", def(value) update_motors() end)
tasmota.add_rule("Power5#State", def(value) update_motors() end)
tasmota.add_rule("Power6#State", def(value) update_motors() end)
tasmota.add_rule("Power7#State", def(value) update_motors() end)
tasmota.add_rule("Power8#State", def(value) update_motors() end)

print("VSP-WSC-4 motor driver loaded")
