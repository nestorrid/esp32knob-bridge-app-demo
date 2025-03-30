import os

from piedmont import Piedmont
from protoai import Message
from protoai.message import MessageRole


config = os.path.join(os.path.abspath(os.path.curdir), 'g29.yaml')
pie = Piedmont(config)
message = Message('당신은 다국어 어시스턴트입니다. 중국어, 영어, 일본어, 한국어를 사용해야 합니다. ')

gears = ['P', 'R', 'N', 'D']
current_gear = 'P'
current_music_idx = 1
is_music_playing = 0
knob_mode = 0
is_listening = 0


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


@pie.serial('KNOB_PRESSED')
def knob_pressed_handler(data: str):
    global is_music_playing, is_listening
    if knob_mode == 1:
        if is_music_playing == 1:
            pie.send_pp_connection('PAUSE')
            is_music_playing = 0
        else:
            pie.send_pp_connection('PLAY', current_music_idx)
            is_music_playing = 1
    else:
        if is_listening == 0:
            pie.send_pp_connection('wheel-button_r2', uppercase=False)
            is_listening = 1
        else:
            pie.send_pp_connection('wheel-button_r3', uppercase=False)
            is_listening = 0


@pie.serial('KNOB_DOUBLE_PRESSED')
def knob_double_pressed_handler(data: str):
    global knob_mode
    knob_mode = int(data)
    print(f'Current Mode: {knob_mode}')


@pie.serial('KNOB_LONG_PRESSED')
def knob_long_pressed_handler(data: str):
    message.messages = message.messages[:1]
    pie.send_pp_connection('wheel-button_spinner', '0', False)


@pie.bridge('ASK_AI')
def ask_ai_handler(data: str):
    pie.send_pp_connection('WAITING_RESPONSE')
    try:
        result = message.append(data).ask()
        message.append(result, role=MessageRole.ASSISTANT)
        pie.send_pp_connection('AI_ANSWER', result)
    except Exception as e:
        print('Error: {e}')
        pie.send_pp_connection('AI_ANSWER', '很抱歉, 服务器开小差了, 请稍后再试...')


if __name__ == "__main__":

    print("Protopie Connect Demo Bridge App for ESP32-S3 Knob is running...")
    print("Use command + c to quit.")

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("Exit.")
            exit()
