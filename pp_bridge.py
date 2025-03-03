from piedmont import Piedmont
import os

config = os.path.join(os.path.abspath(os.path.curdir), 'config.yaml')

pie = Piedmont(config)


@pie.bridge('test')
def demo(data):
    """
    Send Message: `test` with or without value from Protopie Connect Dashboard to test this handler.
    You will see response in the dashboard.

        Time    Message     Value   Source
        xxx     TEST        aaa     Bridge App

    """
    pie.send_pp_connection('test', 'aaa')


@pie.bridge('message')
def message_handler(data):
    """
    Send Message: `message` with or without value from Protopie Connect Dashboard to test this handler.
    You will see response in the dashboard.

        Time    Message     Value                           Source
        xxx     Responese   Response from Bridge App        Bridge App

    """
    pie.send_pp_connection('Response', 'Response from Bridge App')


@pie.bridge('json')
def returnJson(data):
    """
    Send Message: `json` with or without value from Protopie Connect Dashboard to test this handler.
    You will see response in the dashboard.

        Time    Message     Value                       Source
        xxx     JSONDATA    {"key": "value"}            Bridge App

    """
    pie.send_pp_connection('jsonData', {
        "key": "value"
    })


@pie.serial('KNOB_GEAR_SHIFT')
def gear_shift_handler(data: str):
    pie.send_pp_connection('KNOB_GEAR_SHIFT', data)


@pie.serial('KNOB_ROTATE')
def knob_rotate_handler(data: str):
    pie.send_pp_connection('KNOB_ROTATE', data)


@pie.serial('KNOB_VALUE')
def knob_value_handler(data: str):
    pie.send_pp_connection('KNOB_VALUE', data)


if __name__ == "__main__":

    print("Protopie Connect Demo Bridge App for ESP32-S3 Knob is running...")
    print("Use command + c to quit.")

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("Exit.")
            exit()
