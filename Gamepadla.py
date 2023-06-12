ver = "1.0.2"
print("Gamepadla " + ver + " | https://gamepadla.com")
print("")

import pygame
import time
from tqdm import tqdm
import numpy as np
import platform

print("Based on the method of: https://github.com/chrizonix/XInputTest")
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

repeat = 1984 #1984

def filter_outliers(array):
    lower_quantile = 0.02  # Lower quantile (1%)
    upper_quantile = 0.995  # Upper quantile (99%)

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
    print(f"Rotate left stick without stopping")

if not joystick.get_init():
    print("Controller not connected")
    exit(1)

times = []
start_time = time.time()

prev_x, prev_y = None, None

with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} {n_fmt}/{total_fmt}') as pbar:
    while True:
        pygame.event.pump()

        # Положення стіків в момент оберту
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        
        if not ("0.0" in str(x) and "0.0" in str(y)): # Переконуємося що стік достатньо відхилився (Антидріфт)
            
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
                        if delay != 0.0 and delay > 1.5: #Відсікаємо низькі нереальні значення 
                            times.append(delay)
                            pbar.update(1)
                            delay_list.append(delay)
                        
                        break

            if len(times) >= repeat:
                break

delat_clear = delay_list
#delat_clear.sort() # Сортування
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

# Отримати інформацію про операційну систему
os_name = platform.system()  # Назва операційної системи
os_version = platform.release()  # Версія операційної системи
print(f" ")
print(f"Operating System:   {os_name}")
print(f"OS Version:         {os_version}")

print(f" ")
if input("Save the test result? (Y/N): ").lower() == "y":
    with open('test_results.txt', 'w') as f:
        f.write(f"Gamepadla {ver}\n")
        f.write(f"https://gamepadla.com\n")
        f.write(f" \n")
        f.write(f"Date:         {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        f.write(f"Driver:       {joystick_name}\n")
        f.write(f"OS Name:      {os_name}\n")
        f.write(f"OS Ver.:      {os_version}\n")
        f.write(f" \n")
        f.write(f"Minimal latency:  {filteredMin} ms\n")
        f.write(f"Average latency:  {filteredAverage_rounded} ms\n")
        f.write(f"Maximum latency:  {filteredMax} ms\n")
        f.write(f"Polling Rate:     {polling_rate} Hz\n")
        f.write(f"Jitter [Beta]:    {jitter} ms\n")
        f.write(f" \n")
        f.write(f"Delay List ({len(delat_clear)}): \n{delat_clear}\n")
    print("Test results saved in 'test_results.txt'")