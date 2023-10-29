ver = "3.0.1"
print(f" ")
print(f" ")
print(f"   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ ██╗      █████╗ ")
print(f"  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗██║     ██╔══██╗")
print(f"  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║██║     ███████║")
print(f"  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║██║     ██╔══██║")
print(f"  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝███████╗██║  ██║")
print(f"   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝")
print(f"    Polling Rate Tester " + ver + "                         https://gamepadla.com")
print(f" ")
print(f" ")

import pygame
import time
import numpy as np
import math
import sys

def get_polling_rate_max(actual_rate):
    actual_rate = math.floor(actual_rate)
    polling_rates = [125, 250, 500, 1000]
    closest_rate = min(filter(lambda x: x >= actual_rate, polling_rates))
    return closest_rate

while True:
    pygame.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    if not joysticks:
        print("No controller found")
        time.sleep(10)
        exit(1)
    else:
        print(f" ")
        print(f"Found {len(joysticks)} controller(s)")

        for idx, joystick in enumerate(joysticks):
            print(f"{idx + 1}. {joystick.get_name()}")

        selected_index = input("Please enter the index of the controller you want to test: ")
        try:
            selected_index = int(selected_index) - 1
            if 0 <= selected_index < len(joysticks):
                joystick = joysticks[selected_index]
            else:
                print("Invalid index. Defaulting to the first controller.")
                joystick = joysticks[0]
        except ValueError:
            print("Invalid input. Defaulting to the first controller.")
            joystick = joysticks[0]

        print(f" ")
        print(f"Rotate left stick without stopping.")

    if not joystick.get_init():
        print("Controller not connected")
        exit(1)

    times = []
    last_delay = None
    start_time = time.time()
    last_movement_time = start_time
    has_moved = False

    prev_x, prev_y = None, None

    try:
        while True:
            pygame.event.pump()

            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            
            if x != 0 or y != 0:
                last_movement_time = time.time()
                has_moved = True

                if last_delay is not None:
                    times.append(last_delay)
                    polling_rate = round(1000 / (np.mean(times) if times else 1), 2)
                    stability = round((polling_rate / get_polling_rate_max(polling_rate)) * 100, 2)
                    sys.stdout.write("\033[A\033[KPolling Rate: {:.2f} [{} Hz]   |   Stability: {:.2f}%\n".format(polling_rate, get_polling_rate_max(polling_rate), stability))
                    sys.stdout.flush()
                last_delay = None

                if prev_x is None and prev_y is None:
                    prev_x, prev_y = x, y
                elif x != prev_x or y != prev_y:
                    end_time = time.time()
                    duration = (end_time - start_time) * 1000
                    start_time = end_time
                    prev_x, prev_y = x, y

                    while True:
                        pygame.event.pump()
                        new_x = joystick.get_axis(0)
                        new_y = joystick.get_axis(1)

                        if new_x != x or new_y != y:
                            end = time.time()
                            last_delay = (end - start_time) * 1000
                            break

            if has_moved and time.time() - last_movement_time > 0.5:
                times = []
                start_time = time.time()
                last_delay = None
                last_movement_time = start_time
                has_moved = False
                prev_x, prev_y = None, None

    except KeyboardInterrupt:
        pass

    if times:
        polling_rate = round(1000 / np.mean(times), 2)
        stability = round((polling_rate / get_polling_rate_max(polling_rate)) * 100, 2)
    else:
        polling_rate = 0
        stability = 0
