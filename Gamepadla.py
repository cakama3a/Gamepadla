print("Gamepadla 1.0.1")
import pygame
import time
import base64
from tqdm import tqdm
import numpy as np
import webbrowser

#print("Made by the method of: https://github.com/chrizonix/XInputTest")
print(f" ")
print(f" ")
print(f"   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ ██╗      █████╗ ")
print(f"  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗██║     ██╔══██╗")
print(f"  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║██║     ███████║")
print(f"  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║██║     ██╔══██║")
print(f"  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝███████╗██║  ██║")
print(f"   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝")
print("                                         by John Punch: https://t.me/ivanpunch")
print(f" ")

repeat = 2000

def filter_outliers(array):
    lower_quantile = 0.02  # Lower quantile (2%)
    upper_quantile = 0.98  # Upper quantile (98%)

    sorted_array = sorted(array)
    lower_index = int(len(sorted_array) * lower_quantile)
    upper_index = int(len(sorted_array) * upper_quantile)

    return sorted_array[lower_index:upper_index + 1]

pygame.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
delay_list = []

if not joysticks:
    print("No controller found")
    time.sleep(10)
    exit(1)
else:
    print(f" ")
    print(f"Found {len(joysticks)} of controller(s)")
    
    # Використовуємо перший контролер
    joystick = joysticks[0]
    joystick.init()
    joystick_name = joystick.get_name()
    print(f"Gamepad mode: {joystick_name}")
    print(f" ")
    print(f"Move the left stick in a circular without stopping")

if not joystick.get_init():
    print("Controller not connected")
    exit(1)

times = []
start_time = time.time()

prev_x, prev_y = None, None

with tqdm(total=repeat, ncols=80) as pbar:
    while True:
        pygame.event.pump()

        # Положення стіків в момент оберту
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        
        if not ("0.0" in str(x) and "0.0" in str(y)):
            
            if prev_x is None and prev_y is None:
                prev_x, prev_y = x, y
            elif x != prev_x or y != prev_y:
                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)
                start_time = end_time
                prev_x, prev_y = x, y

                while True:
                    pygame.event.pump()
                    new_x = joystick.get_axis(0)
                    new_y = joystick.get_axis(1)

                    if new_x != x or new_y != y:
                        end = time.time()
                        delay = round((end - start_time) * 1000, 2)
                        #print(delay)
                        if delay != 0.0:
                            times.append(delay)
                            pbar.update(1)
                            delay_list.append(delay)
                        
                        break

            if len(times) >= repeat:
                break

delay_list = filter_outliers(delay_list)

filteredMin = min(delay_list)
filteredMax = max(delay_list)
filteredAverage = np.mean(delay_list)
filteredAverage_rounded = round(filteredAverage, 2)

polling_rate = round(1000 / filteredAverage, 2)

jitter = np.std(delay_list)
jitter = round(jitter, 2)

print(f" ")
print(f"Minimal latency:    {filteredMin} ms")
print(f"Average latency:    {filteredAverage_rounded} ms")
print(f"Maximum latency:    {filteredMax} ms")
print(f"Polling Rate:       {polling_rate} Hz")
print(f"Jitter [Beta]:      {jitter} ms")

url_gen = f"{filteredMin}_{filteredAverage_rounded}_{filteredMax}_{polling_rate}_{joystick_name}"
encoded_url_gen = base64.b64encode(url_gen.encode('utf-8')).decode('utf-8')
url_fin = "https://gamepadla.com/sb_" + encoded_url_gen

print(f" ")
if input("Send the test result to Gamepadla.com? (Y/N): ").lower() == "y":
    webbrowser.open(url_fin)
