# VSP-WSC-4 Window Shade Controller
# Berry script for H-bridge motor control via TB6612FNG
# Upload this file as autoexec.be to Tasmota filesystem
#
# GPIO assignments (physical GPIO numbers):
#   STBY:          GPIO37
#   Shade 1 Open:  GPIO43  (M2_BIN1)
#   Shade 1 Close: GPIO2   (M2_BIN2)
#   Shade 2 Open:  GPIO44  (M1_AIN1)
#   Shade 2 Close: GPIO42  (M1_AIN2)
#   Shade 3 Open:  GPIO36  (M3_AIN1)
#   Shade 3 Close: GPIO35  (M3_AIN2)
#   Shade 4 Open:  GPIO38  (M4_BIN1)
#   Shade 4 Close: GPIO39  (M4_BIN2)

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

# Set all motor pins to output mode and initialize low
var motor_pins = [PIN_S1_OPN, PIN_S1_CLS, PIN_S2_OPN, PIN_S2_CLS,
                  PIN_S3_OPN, PIN_S3_CLS, PIN_S4_OPN, PIN_S4_CLS, PIN_STBY]

for pin : motor_pins
    gpio.pin_mode(pin, gpio.OUTPUT)
    gpio.digital_write(pin, 0)
end

# Enable STBY -- holds HIGH permanently after boot
gpio.digital_write(PIN_STBY, 1)

# Motor control functions
def shade_open(open_pin, close_pin)
    gpio.digital_write(close_pin, 0)
    gpio.digital_write(open_pin, 1)
end

def shade_close(open_pin, close_pin)
    gpio.digital_write(open_pin, 0)
    gpio.digital_write(close_pin, 1)
end

def shade_stop(open_pin, close_pin)
    gpio.digital_write(open_pin, 0)
    gpio.digital_write(close_pin, 0)
end

# Shutter relay state handler
# Tasmota Shutter module drives virtual relay pairs
# Relay 1+2 = Shade 1, Relay 3+4 = Shade 2, etc.
# Relay odd = Open direction, Relay even = Close direction

def power_change(cmd, idx, payload, raw)
    var power = tasmota.get_power()

    # Shade 1 (virtual relay 1=open, 2=close)
    if power[0]        # relay 1 on = open
        shade_open(PIN_S1_OPN, PIN_S1_CLS)
    elif power[1]      # relay 2 on = close
        shade_close(PIN_S1_OPN, PIN_S1_CLS)
    else
        shade_stop(PIN_S1_OPN, PIN_S1_CLS)
    end

    # Shade 2 (virtual relay 3=open, 4=close)
    if power[2]
        shade_open(PIN_S2_OPN, PIN_S2_CLS)
    elif power[3]
        shade_close(PIN_S2_OPN, PIN_S2_CLS)
    else
        shade_stop(PIN_S2_OPN, PIN_S2_CLS)
    end

    # Shade 3 (virtual relay 5=open, 6=close)
    if power[4]
        shade_open(PIN_S3_OPN, PIN_S3_CLS)
    elif power[5]
        shade_close(PIN_S3_OPN, PIN_S3_CLS)
    else
        shade_stop(PIN_S3_OPN, PIN_S3_CLS)
    end

    # Shade 4 (virtual relay 7=open, 8=close)
    if power[6]
        shade_open(PIN_S4_OPN, PIN_S4_CLS)
    elif power[7]
        shade_close(PIN_S4_OPN, PIN_S4_CLS)
    else
        shade_stop(PIN_S4_OPN, PIN_S4_CLS)
    end
end

# Register power change handler
tasmota.add_rule("Power#Boot", def() end)  # dummy to wake rules engine
tasmota.add_driver(power_change)

print("VSP-WSC-4 motor driver loaded")
