from piedmont import Piedmont
import os
import logging

config = os.path.join(os.path.abspath(os.path.curdir), 'g29.yaml')
pie = Piedmont(config)

gears = ['P', 'R', 'N', 'D']
current_gear = 'P'
current_music_idx = 1
is_music_playing = 0
is_gear_shift_mode = 1


@pie.serial('KNOB_GEAR_SHIFT')
def gear_shift_handler(data: str):
    global current_gear
    last_idx = gears.index(current_gear)
    new_idx = gears.index(data)

    if last_idx == new_idx:
        return
    elif last_idx > new_idx:
        pie.send_pp_connection('wheel-shift_left', "", False)
    else:
        pie.send_pp_connection('wheel-shift_right', "", False)
    current_gear = data


@pie.serial('KNOB_ROTATE')
def knob_rotate_handler(data: str):
    global current_music_idx
    if is_music_playing:
        last_idx = current_music_idx
        if data == '+':
            current_music_idx = min(current_music_idx + 1, 10)
        elif data == '-':
            current_music_idx = max(current_music_idx - 1, 1)
        if last_idx == current_music_idx:
            return
        pie.send_pp_connection('PLAY', current_music_idx)


@pie.serial('MESSAGE_KNOB_PRESSED')
def knob_pressed_handler(data: str):
    global is_music_playing
    if is_gear_shift_mode == 0:
        if is_music_playing == 1:
            pie.send_pp_connection('PAUSE')
            is_music_playing = 0
        else:
            pie.send_pp_connection('PLAY', current_music_idx)
            is_music_playing = 1


@pie.serial('MESSAGE_KNOB_DOUBLE_PRESSED')
def knob_double_pressed_handler(data: str):
    global is_gear_shift_mode
    is_gear_shift_mode = (is_gear_shift_mode + 1) % 2
    print(f'KNOB MODE: {is_gear_shift_mode}')


@pie.serial('MESSAGE_KNOB_LONG_PRESSED')
def knob_long_pressed_handler(data: str):
    pie.send_pp_connection('wheel-button_spinner', '0', False)


if __name__ == "__main__":

    print("Protopie Connect Demo Bridge App for ESP32-S3 Knob is running...")
    print("Use command + c to quit.")

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("Exit.")
            exit()
