#!/usr/bin/env python

import time
import datetime

import RPi.GPIO as GPIO

import opc

ADDRESS = 'localhost:7890'
BUTTON_GPIO = 4

RIGHT_SIDE = 2
LEFT_SIDE = 4
CENTER = 3

CENTER_BOTTOM = 10
CENTER_MIDDLE = CENTER_BOTTOM + 10

PINK = (255, 105, 180)
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


def button_pressed(channel):
    global was_button_pressed, last_center_update, heart_state, pixels
    was_button_pressed = True
    last_center_update = datetime.datetime.now()
    if heart_state > 0:
        heart_state -= 1
        update_center_state(pixels, heart_state)
        client.put_pixels(pixels, channel=0)


was_button_pressed = False
last_center_update = datetime.datetime.now() - datetime.timedelta(hours=1)
pixels = []
heart_state = 3
client = opc.Client(ADDRESS)

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_pressed, bouncetime=500)


def update_center_state(pixels, heart_state):
    if heart_state == 3:
        pixels[CENTER * 64:(CENTER + 1) * 64] = [RED] * 64
    elif heart_state == 2:
        pixels[CENTER * 64:(CENTER + 1) * 64] = [RED] * CENTER_MIDDLE + [BLACK] * (64 - CENTER_MIDDLE)
    elif heart_state == 1:
        pixels[CENTER * 64:(CENTER + 1) * 64] = [RED] * CENTER_BOTTOM + [BLACK] * (64 - CENTER_BOTTOM)
    elif heart_state == 0:
        pixels[CENTER * 64:(CENTER + 1) * 64] = [(0, 0, 0)] * 64


def heartbeat_on_side(pixels, client, animation_state, side):
    brightness = 95 + 40 * animation_state

    # on
    pixels[side * 64:(side + 1) * 64] = [(brightness, 0, 0)] * 64
    client.put_pixels(pixels, channel=0)
    time.sleep(0.2)
    # off
    pixels[side * 64:(side + 1) * 64] = [PALE_RED] * 64
    client.put_pixels(pixels, channel=0)
    time.sleep(0.2)
    # on
    pixels[side * 64:(side + 1) * 64] = [(brightness, 0, 0)] * 64
    client.put_pixels(pixels, channel=0)
    time.sleep(0.2)
    # off
    pixels[side * 64:(side + 1) * 64] = [PALE_RED] * 64
    client.put_pixels(pixels, channel=0)
    time.sleep(0.5)


def advance_broken_heart_animation(pixels, client, animation_state):
    if animation_state < 4:
        heartbeat_on_side(pixels, client, animation_state, RIGHT_SIDE)
    else:
        heartbeat_on_side(pixels, client, animation_state - 4, LEFT_SIDE)


def play_mended_heart_animation(pixels, client):
    for i in range(64):
        pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = [PINK] * i + [BLACK] * (64 - i)
        pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = [PINK] * i + [BLACK] * (64 - i)
        client.put_pixels(pixels, channel=0)
        time.sleep(0.05)

    current_strip = [PINK] * 64
    for i in range(8):
        for j in range(8):
            del current_strip[-1]
            current_strip.insert(0, RAINBOW_8_COLORS[i])
            pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = current_strip
            pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = current_strip
            client.put_pixels(pixels, channel=0)
            time.sleep(0.01 + (((8*i) + j) * 0.002))

    for i in range(4):
        pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = [PINK] * 64
        pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = [PINK] * 64
        client.put_pixels(pixels, channel=0)
        time.sleep(0.2)
        pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = current_strip
        pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = current_strip
        client.put_pixels(pixels, channel=0)
        time.sleep(0.2)
        pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = [PINK] * 64
        pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = [PINK] * 64
        client.put_pixels(pixels, channel=0)
        time.sleep(0.2)
        pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = current_strip
        pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = current_strip
        client.put_pixels(pixels, channel=0)
        time.sleep(0.5)

    pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = current_strip
    pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = current_strip
    client.put_pixels(pixels, channel=0)

    for i in range(3):
        time.sleep(1.5)
        update_center_state(pixels, i+1)
        client.put_pixels(pixels, channel=0)

    time.sleep(1.5)

    for _ in range(255):
        for pixel in range(64):
            current_strip[pixel] = tuple((intensity - 1) if intensity > 0 else 0 for intensity in current_strip[pixel])
            pixels[RIGHT_SIDE * 64:(RIGHT_SIDE + 1) * 64] = current_strip
            pixels[LEFT_SIDE * 64:(LEFT_SIDE + 1) * 64] = current_strip
        client.put_pixels(pixels, channel=0)
        time.sleep(0.01)


def main():
    global was_button_pressed, pixels, heart_state, client
    pixels = [(0, 0, 0) for _ in range(512)]
    animation_state = 0

    update_center_state(pixels, heart_state)

    while True:
        if was_button_pressed:
            was_button_pressed = False
            if heart_state == 0:
                play_mended_heart_animation(pixels, client)
                heart_state = 3
                update_center_state(pixels, heart_state)
                animation_state = 0
        elif heart_state < 3:
            if datetime.datetime.now() - last_center_update > datetime.timedelta(seconds=5):
                heart_state += 1
                update_center_state(pixels, heart_state)
        advance_broken_heart_animation(pixels, client, animation_state)
        client.put_pixels(pixels, channel=0)
        animation_state += 1
        if animation_state == 8:
            animation_state = 0


if __name__ == '__main__':
    main()
