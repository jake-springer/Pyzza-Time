

from machine import I2C, Pin
from utime import sleep
from pico_i2c_lcd import I2cLcd

buzzer = Pin(18, Pin.OUT)

# I2C Pinout (phys, gpio)
# GND = black, 38, ground
# VCC = orange, 40, VBUS
# SDA = white, 21, 16
# SCL = blue, 22,

# top left brown
# tr white
# br purp
# bl blue

lcd_freq = 400000
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=lcd_freq)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)


def feedback():
    buzzer.value(1)
    sleep(0.2)
    buzzer.value(0)


def refresh_lcd():
    seg1 = ""
    seg2 = "" 
    seg3 = ""
    seg4 = ""
    segs = [seg1, seg2, seg3, seg4]

    lcd.clear()    
    for t in t_list:
        segs[t_list.index(t)] = t.display_value
    row1 =  clean_spacing(segs[0], segs[1]) + '\n'
    row2 = clean_spacing(segs[2], segs[3])

    lcd.putstr(row1)
    lcd.putstr(row2)



class Timer:
    def __init__(self, timer_id):
        self.timer_id = timer_id
        self.start_time = 420 # Total seconds to run (7 min * 60 sec = 420)
        self.run_time = self.start_time # time active
        self.interval = 0.1 # time between loops
        self.display_value = "OFF"
        self.active = False
        self.done = False

    def reset(self):
        self.done = False
        self.active = False
        self.run_time = self.start_time
        self.display()
        refresh_lcd()

    def start(self):
        if self.done:
            self.reset()
            feedback()
        else:
            self.active = True
            feedback()
            self.display()
            refresh_lcd()
            
    def count(self):
        if self.active:
            self.run_time -= self.interval
            if self.run_time <= 0:
                self.finish()
            else:
                self.display()
                return self.run_time

    def finish(self):
        print(f"[>] Timer {str(self.timer_id)} has finished.")
        self.run_time = 0
        self.done = True
        self.active = False
        self.display()
        refresh_lcd()
        
    def display(self):
        if self.done:
            self.display_value = "DONE"
            return
        if not self.active:
            self.display_value = "OFF"
            return
        if self.run_time < 60:
            self.display_value = str(int(self.run_time)) + " sec"
        else:
            self.display_value = str(round(int(self.run_time) / 60, 1)) + " min"



b1 = Pin(0, Pin.IN, Pin.PULL_UP) 
b2 = Pin(1, Pin.IN, Pin.PULL_UP)
b3 = Pin(2, Pin.IN, Pin.PULL_UP)
b4 = Pin(3, Pin.IN, Pin.PULL_UP)

b_list = [b1,b2,b3,b4]
t_list = [
    Timer(1),
    Timer(2),
    Timer(3),
    Timer(4)
    ]

# b.value == 0 when pressed

def clean_spacing(i1, i2):
    max_len = 16
    l1 = len(i1)
    l2 = len(i2)
    total_chars = l1 + l2
    space = " " * (max_len - total_chars)
    return i1 + space + i2
feedback()
lcd.clear()
lcd.putstr("Pizza time :)")
sleep(5)


feedback()
loop = 0
refresh_lcd()

while True:
    is_done = False
    buzzer.value(0)
    loop += 1
    
    # Evaluate buttons
    for b in b_list:
        if b.value() == 0:
            refresh_lcd()
            btn = b_list.index(b)
            timer = t_list[btn]
            print(f"Button {str(btn)} pressed")
            if not timer.active:
                t_list[btn].start()
    
    # Run timers
    for t in t_list:
        t.count()
        if t.done:
            is_done = True
        print("> Timer: " + str(t.timer_id))
        print("> Time remaining: " + str(t.run_time))
        print()
    print("=============================================")
    if is_done:
        buzzer.value(1)
    sleep(0.1)
    if loop % 300 == 0:
        refresh_lcd()
    if loop >= 300000000:
        loop = 0
    
    
    