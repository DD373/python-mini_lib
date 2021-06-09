import logging
import requests
import random
from threading import Thread
from selenium import webdriver
import pyautogui
from time import sleep
import os
from ftplib import FTP


def logging_ini(type='info'):
    """Логгирование

    Включаем логгирование с указанием type - типа:
    debug - самый низкий тип, используется для разработки
    info - рекомендуемый тип, все оповещения
    Запись производится в файл work_files\\backup\\log.txt
    Возвращает имя созданного логера"""

    if type == "debug":
        logging.basicConfig(
            level=logging.DEBUG,
            filename=r'work_files\backup\log.txt',
            filemode='w+',
            format="%(asctime)s - [%(levelname)s] - %(name)s - [%(threadName)s] - %(funcName)s(%(lineno)d) - %(message)s",
        )
    if type == "info":
        logging.basicConfig(
            level=logging.INFO,
            filename=r'work_files\backup\log.txt',
            filemode='w+',
            format="%(asctime)s - [%(levelname)s] - %(name)s - [%(threadName)s] - %(funcName)s(%(lineno)d) - %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.ERROR,
            filename=r'work_files\backup\log.txt',
            filemode='w+',
            format="%(asctime)s - [%(levelname)s] - %(name)s - [%(threadName)s] - %(funcName)s(%(lineno)d) - %(message)s",
        )
    return logging.getLogger(__name__)


def build_unique_list_keep_order(seq):
    """Удаление дубликатов из списка

    На вход подяется seq - список, а на выходе без дублей
    """
    logger.debug("Remove all dublicates from list")
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def get_proxy(proxy_path=r'work_files\input\proxy.txt'):
    """Взять прокси из файла

    Получаем случайный прокси из файла по этому пути proxy_path"""
    max_list = 0
    result = ""

    with open(f'{proxy_path}', "r") as file:
        old = file.read().splitlines()
        max_list = len(old)
        item = random.randint(0, max_list - 1)
        result = old[item]
        logger.debug("New proxy received : " + result)
    return result


def get_ua():
    """Взять юзерагент из файла

    Получаем случайный юзерагент из файла"""
    max_list = 0
    result = ""

    with open(r"work_files\input\useragents_list.txt", "r") as file:
        old = file.read().splitlines()
        max_list = len(old)
        item = random.randint(0, max_list - 1)
        result = old[item]
        logger.debug("New user agent received : " + result)
    return result  # '\'' + result + '\''


def error_save(url_1, url_2, _type):
    """Запись лога ошибки

    url_1 - ссылка на родителя(основной сайт),
    url_2 - ссылка на текущую страницу,
    _type - тип ошибки(свой комментарий)"""

    logger.error("Error in url :" + url_2 + "Type :" + _type, exc_info=True)

    # Проверяем есть ли папка output, если нет то создаем ее
    if not os.path.isdir(r'work_files\output'):
        os.mkdir(r'work_files\output')

    fb = open(r'work_files\output\bad_url.txt', 'a+')
    fb.write(str(url_1) + ';' + str(url_2) + ';' + _type + '\n')
    fb.close()


def send_fttp(file_path, ftp_path, file_type='TXT', serv='products.shping.com', lgn='efimenco', psw='Wwrm7MtAa65cBFJvus9c8PMBq3mnPsyw', port=21):
    """Функция для загрузки файлов на FTP-сервер
    
    @param file_path: Путь к файлу для загрузки
    @param ftp_path: Путь на сервере куда загружать
    @param file_type: тип файла TXT PDF
    @param serv: имя сервера фтп
    @param lgn: имя пользователя на фтп
    @param psw: пароль пользователя на фтп
    @param port: порт подключения на фтп"""    
  
    ftp = FTP(serv)
    ftp.login(lgn, psw)

    ftp.cwd(ftp_path)
    if file_type == 'TXT':
        with open('work_files\\output\\' + file_path) as fobj:
            ftp.storlines('STOR ' + file_path, fobj)
    else:
        with open('work_files\\output\\' + file_path, 'rb') as fobj:
            ftp.storbinary('STOR ' + file_path, fobj, 1024)    
    
    data = ftp.nlst()
    ftp.quit()

    # Проверяем есть ли папка output, если нет то создаем ее
    if not os.path.isdir(r'work_files\output'):
        os.mkdir(r'work_files\output')

    fb = open(r'work_files\output\ftp_res.txt', 'w')
    for item in data:
        fb.write(str(item) + '\n')
    fb.close()


def multi_thread(func, thread_max=1):
    """Запуск многопотока

    func - функция которая будет запускаться в многопотоке,
    thread_max - количество потоков для запуска
    Функция запускаяется с аргументом = имя потока"""
    potok = []  # массив потоков

    for x in range(thread_max):
        potok.append(Thread(target=func, args=('t' + str(x),)))

    for thr in potok:
        thr.start()

    for thr in potok:
        thr.join()


def get_data_with_selenium(url, load_wait=25, pause_after=5, proxy_enable=True, proxy_path=r'work_files\input\proxy.txt'):
    """Загружаем страницу в браузере с селеникмом

    url - ссылка на нужную страницу,
    load_wait - ожидание загрузки страницы (int),
    pause_after - пауза после загрузки страницы (int),
    proxy_enable - использовать ли прокси (True False),
    proxy_path - пусть на файл со списком прокси"""

    # Proxy settings
    if proxy_enable:
        PROXY = get_proxy(proxy_path)
        logger.debug("Получили прокси:" + PROXY)
        # Find login pass in proxy
        try:
            proxy_host_port = PROXY.split('@')[1]
            logger.debug("Получили proxy_host_port:" + proxy_host_port)
            proxy_user_pass = PROXY.split('@')[0]
            logger.debug("Получили proxy_user_pass:" + proxy_user_pass)
            proxy_user_pass = proxy_user_pass.replace(r"http://", "")
            proxy_user_pass = proxy_user_pass.replace(r"https://", "")
            proxy_user = proxy_user_pass.split(':')[0]
            proxy_pass = proxy_user_pass.split(':')[1]
            logger.debug("Получили proxy_user:" + proxy_user)
            logger.debug("Получили proxy_pass:" + proxy_pass)
            PROXY = proxy_host_port
        except:
            proxy_user, proxy_pass = "", ""
    else:
        PROXY = ''

    # Browser settings
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={get_ua()}')
    if proxy_enable:
        options.add_argument('--proxy-server=%s' % PROXY)

    try:
        # Init browser
        driver = webdriver.Chrome(
            executable_path=r"work_files\input\chromedriver.exe",
            options=options
        )
        driver.set_page_load_timeout(load_wait)

        # Load link
        driver.get(url=url)
        sleep(2)

        if proxy_enable and proxy_user != '':
            sleep(1)
            pyautogui.typewrite(proxy_user)
            pyautogui.press('tab')
            sleep(0.5)
            pyautogui.typewrite(proxy_pass)
            pyautogui.press('enter')

        sleep(pause_after)
        return driver.page_source, driver.get_cookies()

    except Exception as ex:
        logger.exception("Selenium Chrome error")
    finally:
        driver.close()
        driver.quit()


def add_some_trys(func):
    def surrogate(*args, **kwargs):
        i = 0
        this_url = args[0]
        url = args[2]
        result = 'error'
        http_try_max = args[4]
        logger.debug(http_try_max)
        while i < http_try_max:
            logger.debug(f"Get href = {this_url} try {i}")

            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"Get href = {this_url} try {i} reguest code: [{result.status_code}]")
                if result.status_code == 200:
                    # print('Good get')
                    break
            except:
                logger.exception(f"Whith get href = {this_url}")

            i += 1

        else:
            if (url == this_url or this_url == ''):
                error_save(url, this_url, "get main url failed. exit programm")
                SystemExit(1)
            else:
                error_save(url, this_url, "all tries of reguest is end")
                result = 'error'
        return result
    return surrogate


def remove_old_files(*args):
    """Удаляем старые файлы

    args - имена файлов без расширения(только txt)"""
    for arg in args:
        f = open(f'work_files\\output\\{arg}.txt', 'w+')
        f.close()


logger = logging_ini("debug")


# @add_some_trys
# def get_http(input_url, proxy_enable, url, proxy_path=r'work_files\input\proxy.txt', http_try_max=3, cookies=''):
#     """ Get запрос

#     input_url - ссылка для запроса,
#     proxy_enable - использовать прокси True False,
#     url - хост ссылка/родительская (для логирования),
#     proxy_path - путь к файлу с прокси,
#     http_try_max - число попыток пройти по ссылке,
#     cookies - кукисы для запроса"""

#     logger.debug('Start get')
#     if proxy_enable:
#         proxy = get_proxy(proxy_path)
#         proxies = {"http": "http://" + proxy}
#     else:
#         proxies = {}
#     logger.debug(proxies)
#     ua = get_ua()
#     headers = {'user-agent': "'" + ua + "'"}

#     if cookies == "":
#         response = requests.get(input_url, headers=headers, proxies=proxies)
#     else:
#         response = requests.get(input_url, headers=headers, proxies=proxies, cookies=cookies)
#     return response

# @add_some_trys
# def post_http(input_url, proxy_enable, url, proxy_path=r'work_files\input\proxy.txt', http_try_max=3, cookies='', data):
#     """ Get запрос

#     input_url - ссылка для запроса,
#     proxy_enable - использовать прокси True False,
#     url - хост ссылка/родительская (для логирования),
#     proxy_path - путь к файлу с прокси,
#     http_try_max - число попыток пройти по ссылке,
#     cookies - кукисы для запроса"""

#     logger.debug('Start post')
#     if proxy_enable:
#         proxy = get_proxy(proxy_path)
#         proxies = {"http": "http://" + proxy}
#     else:
#         proxies = {}
#     logger.debug(proxies)
#     ua = get_ua()
#     headers = {'user-agent': "'" + ua + "'"}

#     if cookies == "":
#         response = requests.post(input_url, headers=headers, proxies=proxies, data=data)
#     else:
#         response = requests.post(input_url, headers=headers, proxies=proxies, cookies=cookies, data=data)
#     return response