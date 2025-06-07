#!/usr/bin/env micropython

import time
import utime
from machine import Pin
import neopixel

# GPIO Configuration
BUTTON_GPIO = 19
RIGHT_SIDE_GPIO = 18
LEFT_SIDE_GPIO = 17
CENTER_GPIO = 4

# Strip configuration
LEDS_PER_STRIP = 64

# Color definitions
PINK = (255, 50, 127)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PALE_RED = (30, 0, 0)

RAINBOW_8_COLORS = [PINK,
                    (148, 0, 211),
                    (75, 0, 130),
                    (0, 0, 255),
                    (0, 255, 0),
                    (255, 255, 0),
                    (255, 127, 0),
                    (255, 0, 0)]

# Global variables
was_button_pressed = False
last_button_time = 0  # For debouncing

# Initialize NeoPixel strips
right_strip = neopixel.NeoPixel(Pin(RIGHT_SIDE_GPIO), LEDS_PER_STRIP)
left_strip = neopixel.NeoPixel(Pin(LEFT_SIDE_GPIO), LEDS_PER_STRIP)
center_strip = neopixel.NeoPixel(Pin(CENTER_GPIO), LEDS_PER_STRIP)

# Initialize button
button = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)

def button_pressed(pin):
    global was_button_pressed, last_button_time
    
    # Double-check the pin is actually LOW (button really pressed)
    if pin.value() != 0:
        return  # False trigger - pin isn't actually LOW
    
    # Debouncing - ignore if button was pressed recently
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_time) < 300:  # 300ms debounce
        return
    
    # Wait a bit and check again to make sure it's a real press
    time.sleep(0.01)  # 10ms delay
    if pin.value() != 0:
        return  # Button not held down - likely just noise
    
    last_button_time = current_time
    print("Button pressed - starting mending animation!")
    was_button_pressed = True

# Set up button interrupt
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

def set_strip_color(strip, color, start=0, end=None):
    """Set a range of LEDs in a strip to a specific color"""
    if end is None:
        end = LEDS_PER_STRIP
    for i in range(start, min(end, LEDS_PER_STRIP)):
        strip[i] = color

def fill_strip(strip, colors):
    """Fill a strip with a list of colors"""
    for i, color in enumerate(colors[:LEDS_PER_STRIP]):
        strip[i] = color

def update_all_strips():
    """Write all strip changes to the LEDs"""
    right_strip.write()
    left_strip.write()
    center_strip.write()

def heartbeat_both_sides(animation_state):
    """Animate heartbeat on both sides simultaneously"""
    brightness = 95 + 40 * (animation_state % 4)  # Cycle through 4 brightness levels

    # Both sides on
    set_strip_color(right_strip, (brightness, 0, 0))
    set_strip_color(left_strip, (brightness, 0, 0))
    right_strip.write()
    left_strip.write()
    time.sleep(0.2)
    
    # Both sides off
    set_strip_color(right_strip, PALE_RED)
    set_strip_color(left_strip, PALE_RED)
    right_strip.write()
    left_strip.write()
    time.sleep(0.2)
    
    # Both sides on again
    set_strip_color(right_strip, (brightness, 0, 0))
    set_strip_color(left_strip, (brightness, 0, 0))
    right_strip.write()
    left_strip.write()
    time.sleep(0.2)
    
    # Both sides off
    set_strip_color(right_strip, PALE_RED)
    set_strip_color(left_strip, PALE_RED)
    right_strip.write()
    left_strip.write()
    time.sleep(0.5)

def play_wedding_mending_animation():
    """Play the heart mending animation for wedding (no center restoration)"""
    print("Playing wedding mending animation...")
    
    # Fill both sides with pink gradually
    for i in range(LEDS_PER_STRIP):
        set_strip_color(right_strip, PINK, 0, i)
        set_strip_color(right_strip, BLACK, i)
        set_strip_color(left_strip, PINK, 0, i)
        set_strip_color(left_strip, BLACK, i)
        right_strip.write()
        left_strip.write()
        time.sleep(0.05)

    # Create rainbow effect
    current_strip = [PINK] * LEDS_PER_STRIP
    for i in range(8):
        for j in range(8):
            current_strip.pop()
            current_strip.insert(0, RAINBOW_8_COLORS[i])
            fill_strip(right_strip, current_strip)
            fill_strip(left_strip, current_strip)
            right_strip.write()
            left_strip.write()
            time.sleep(0.01 + (((8*i) + j) * 0.002))

    # Flashing effect
    for i in range(4):
        set_strip_color(right_strip, PINK)
        set_strip_color(left_strip, PINK)
        right_strip.write()
        left_strip.write()
        time.sleep(0.2)
        
        fill_strip(right_strip, current_strip)
        fill_strip(left_strip, current_strip)
        right_strip.write()
        left_strip.write()
        time.sleep(0.2)
        
        set_strip_color(right_strip, PINK)
        set_strip_color(left_strip, PINK)
        right_strip.write()
        left_strip.write()
        time.sleep(0.2)
        
        fill_strip(right_strip, current_strip)
        fill_strip(left_strip, current_strip)
        right_strip.write()
        left_strip.write()
        time.sleep(0.5)

    # Final rainbow state - stay like this!
    fill_strip(right_strip, current_strip)
    fill_strip(left_strip, current_strip)
    right_strip.write()
    left_strip.write()
    
    print("Wedding mending animation complete - heart is beautifully mended!")
    
    # Hold the beautiful rainbow state for a while
    time.sleep(3.0)

    # Gentle fade out rainbow back to normal heartbeat
    for fade_step in range(255):
        for pixel in range(LEDS_PER_STRIP):
            r, g, b = current_strip[pixel]
            current_strip[pixel] = (max(0, r-1), max(0, g-1), max(0, b-1))
        fill_strip(right_strip, current_strip)
        fill_strip(left_strip, current_strip)
        right_strip.write()
        left_strip.write()
        time.sleep(0.01)

def main():
    global was_button_pressed
    animation_state = 0

    # Initialize - center strip stays off, both sides start beating
    set_strip_color(center_strip, BLACK)
    center_strip.write()

    print("Wedding Heart LED controller started...")
    print("Heart is beating as one - ready for the celebration!")

    while True:
        try:
            if was_button_pressed:
                was_button_pressed = False
                play_wedding_mending_animation()
                animation_state = 0
            
            # Both sides beat together
            heartbeat_both_sides(animation_state)
            animation_state += 1
            if animation_state == 8:
                animation_state = 0
                
        except KeyboardInterrupt:
            print("Shutting down...")
            # Turn off all LEDs
            set_strip_color(right_strip, BLACK)
            set_strip_color(left_strip, BLACK)
            set_strip_color(center_strip, BLACK)
            update_all_strips()
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(1)

if __name__ == '__main__':
    main() 