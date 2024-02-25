ver = "1.1.0"
from colorama import Fore, Back, Style
import time
import json
from tqdm import tqdm
import numpy as np
import platform
import requests
import uuid
import webbrowser

print(f" ")
print(f" ")
print("   ██████╗  █████╗ ███╗   ███╗███████╗██████╗  █████╗ ██████╗ " + Fore.CYAN + "██╗      █████╗ " + Fore.RESET)
print("  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔══██╗" + Fore.CYAN + "██║     ██╔══██╗" + Fore.RESET)
print("  ██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝███████║██║  ██║" + Fore.CYAN + "██║     ███████║" + Fore.RESET)
print("  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██║██║  ██║" + Fore.CYAN + "██║     ██╔══██║" + Fore.RESET)
print("  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║██████╔╝" + Fore.CYAN + "███████╗██║  ██║" + Fore.RESET)
print("   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═════╝ " + Fore.CYAN + "╚══════╝╚═╝  ╚═╝" + Fore.RESET)
print(Fore.CYAN + "    " + "Gamepadla Tester" + Fore.RESET + "  " + ver + "                           https://gamepadla.com")
print(f" ")
print(f" ")
print(f"Credits:")
print("Based on the method of: https://github.com/chrizonix/XInputTest")
import pygame

#repeat = 1984 #1984

def filter_outliers(array):
    lower_quantile = 0.02   # Lower quantile (1%)
    upper_quantile = 0.995  # Upper quantile (99%)

    sorted_array = sorted(array)
    lower_index = int(len(sorted_array) * lower_quantile)
    upper_index = int(len(sorted_array) * upper_quantile)

    return sorted_array[lower_index:upper_index + 1]

while True:
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

        joystick.init()
        joystick_name = joystick.get_name()
        print(f"Gamepad mode:       {joystick_name}")
         # Отримати інформацію про операційну систему
        os_name = platform.system()  # Назва операційної системи
        os_version = platform.release()  # Версія операційної системи
        print(f"Operating System:   {os_name}")

        repeat = 1988
        repeatq = input("Please select number of tests (1. 2000, 2. 4000, 3. 6000), or enter your own number: ")
        if repeatq == "1":
            repeat = 2000
        elif repeatq == "2":
            repeat = 4000
        elif repeatq == "3":
            repeat = 6000
        else:
            try:
                repeat = int(repeatq)
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # print(f"Connected by:       {connection}")
        #print(f"OS Version:         {os_version}")
        print(f" ")
        print(f"Rotate left stick without stopping")

    if not joystick.get_init():
        print("Controller not connected")
        exit(1)

    times = []
    start_time = time.time()

    prev_x, prev_y = None, None

    with tqdm(total=repeat, ncols=76, bar_format='{l_bar}{bar} {postfix[0]}', postfix=[0]) as pbar:
        while True:
            pygame.event.pump()
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            pygame.event.clear()
            
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
                        pygame.event.clear()

                        if new_x != x or new_y != y:
                            end = time.time()
                            delay = round((end - start_time) * 1000, 2)
                            #print(delay)
                            if delay != 0.0 and delay > 0.2 and delay < 150:  #Відсікаємо низькі нереальні значення 
                                times.append(delay * 1.057) # Відіймаємо 5% * 1.057
                                pbar.update(1)
                                pbar.postfix[0] = "{:05.2f} ms".format(delay)
                                delay_list.append(delay)
                            
                            break

                if len(times) >= repeat:
                    break

    delay_clear = delay_list
    #delay_clear.sort() # Сортування
    str_of_numbers = ', '.join(map(str, delay_clear))
    delay_list = filter_outliers(delay_list)

    filteredMin = min(delay_list)
    filteredMax = max(delay_list)
    filteredAverage = np.mean(delay_list)
    filteredAverage_rounded = round(filteredAverage, 2)

    polling_rate = round(1000 / filteredAverage, 2)

    jitter = np.std(delay_list)
    jitter = round(jitter, 2)

    # Розрахунок максиально можливого полінг рейту на базі існуючого
    def get_polling_rate_max(actual_rate):
        max_rate = 125
        if actual_rate > 150:
            max_rate = 250
        if actual_rate > 320:
            max_rate = 500 
        if actual_rate > 600:
            max_rate = 1000
        return max_rate

    print(f" ")
    max_polling_rate = get_polling_rate_max(polling_rate)
    print(f"Polling Rate Max.:  {max_polling_rate} Hz")
    print(f"Polling Rate Avg.:  {polling_rate} Hz")
    stablility = round((polling_rate/max_polling_rate)*100, 2)
    print(f"Stability:          {stablility}%")

    print(f" ")
    print(f"=== Synthetic tests ===")
    print(f"Minimal latency:    {filteredMin} ms")
    print(f"Average latency:    {filteredAverage_rounded} ms")
    print(f"Maximum latency:    {filteredMax} ms")
    print(f"Jitter:             {jitter} ms")
    #print(f"Data:      {delay_clear} ms")

    # Генеруємо унікальний ключ ідентифікатора
    test_key = uuid.uuid4()

    print(f" ")
    data = {
        'test_key': str(test_key),
        'version': ver,
        'url': 'https://gamepadla.com',
        'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'driver': joystick_name,
        'os_name': os_name,
        'os_version': os_version,
        'min_latency': filteredMin,
        'avg_latency': filteredAverage_rounded,
        'max_latency': filteredMax,
        'polling_rate': polling_rate,
        'jitter': jitter,
        'mathod': 'GP',
        'delay_list': str_of_numbers
    }

    # Записуємо дані в файл з відступами для кращої читабельності
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile, indent=4)

     # Використовуйте це:
    if input("Open in browser? (Y/N): ").lower() == "y":
        gamepad_name = input("Please enter the name of your gamepad: ")
        connection = input("Please select connection type (1. Cable, 2. Bluetooth, 3. Dongle): ")
        if connection == "1":
            connection = "Cable"
        elif connection == "2":
            connection = "Bluetooth"
        elif connection == "3":
            connection = "Dongle"
        else:
            print("Invalid choice. Defaulting to Cable.")
            connection = "Unset"

        # Додаэмо данні в масив
        data['connection'] = connection  
        data['name'] = gamepad_name

        response = requests.post('https://gamepadla.com/scripts/poster.php', data=data)
        if response.status_code == 200:
            print("Test results successfully sent to the server.")
            # Перенаправляємо користувача на сторінку з результатами тесту
            webbrowser.open(f'https://gamepadla.com/result/{test_key}/')
        else:
            print("Failed to send test results to the server.")

    # Видаляємо непотрібні ключі
    del data['test_key']
    del data['os_version']
    del data['url']

    # Використовуйте це:
    if input("Run again? (Y/N): ").lower() != "y":
        break