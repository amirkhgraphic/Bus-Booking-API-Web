import json
import re
import requests
from itertools import count
from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask

app = Flask(__name__)


@app.route('/ticket/', methods=['GET'])
def ticket_api():
    input_ = str(request.args.get('info')).split('/')
    url = f'https://payaneh.ir/bus/index/{input_[0].title()}/{input_[1].title()}?date={"-".join(input_[2].split())}'
    # print(url)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like" \
                 " Gecko) Chrome/114.0.0.0 Safari/537.36"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("user-agent=" + user_agent)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    dic = dict()
    try:
        for i in count(1):
            info = driver.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div/div[{i}]/div')

            seats = info.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div'
                                                                f'/div[{i}]/div/div[2]/div/'
                                                                f'small').text.split(':')[1].strip()

            if seats == '۰':
                continue

            dic[i] = dict()

            dic[i]['company_name'] = info.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div'
                                                                 f'/div[{i}]/div/div[1]/div[1]/div[1]/div/div'
                                                                 f'[2]/div/p[1]').text
            dic[i]['bus_type'] = info.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div[2]'
                                                             f'/div/div[{i}]/div/div[1]/div[1]/div[1]/div/'
                                                             f'div[2]/div/p[2]').text
            dic[i]['departure_time'] = info.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div[2]'
                                                                   f'/div/div[{i}]/div/div[1]/div[1]'
                                                                   f'/div[2]/div').text.split('\n')
            dic[i]['price'] = info.find_element(By.XPATH, f'//*[@id="app"]/div[2]/div/div[2]/div/div'
                                                          f'[2]/div/div[{i}]/div/div[2]/div/h5').text
            dic[i]['empty_seats'] = seats
    except:
        pass
    driver.quit()
    return json.dumps(dic, ensure_ascii=False)


@app.route('/weather/', methods=['GET'])
def weather_api():
    input_ = str(request.args.get('info'))
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }

    url = f"https://www.google.com/search?hl=en&lr=lang_en&ie=UTF-8&q=weather%20{input_.title()}"

    text = requests.get(url, headers=headers).text
    data = re.search(r"pmc='({.*?})'", text).group(1)
    data = json.loads(data.replace(r"\x22", '"').replace(r'\\"', r"\""))
    info = data["wobnm"]["wobhl"]
    for i in info:
        date = i["dts"].split()
        if date[0] == 'Monday' and date[1] == '14:00':
            dic = dict()
            dic['weather_circumstance'] = i['c']
            dic['temperature_celsius'] = i['tm']
            dic['temperature_fahrenheit'] = i['t']
            dic['precipitation'] = i['p']
            dic['humidity'] = i['h']
            dic['wind_kmh'] = i['ws'].split()[0]
            dic['wind_mph'] = i['tws'].split()[0]
            return jsonify(dic)


@app.route('/f_translate/', methods=["GET"])
def f_translator():
    input_ = str(request.args.get('info'))
    url = f'https://translate.google.com/?sl=fa&tl=en&text={input_}&op=translate'
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=op)
    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/di'
                                  'v[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button').click()
    return jsonify(driver.find_element(By.CSS_SELECTOR, '#yDmH0d > c-wiz > div > div.WFnNle'
                                                           ' > c-wiz > div.OlSOob > c-wiz > '
                                                           'div.ccvoYb.EjH7wc > div.AxqVh > div.OPPzxe >'
                                                           ' c-wiz.sciAJc > div'
                                                           ' > div.usGWQd').text)


@app.route('/e_translate/', methods=["GET"])
def e_translator():
    input_ = str(request.args.get('info'))
    url = f'https://translate.google.com/?sl=en&tl=fa&text={input_}&op=translate'
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=op)
    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/div/di'
                                  'v[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button').click()
    return json.dumps(driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/'
                                         'div[2]/div[3]/c-wiz[2]/div/div[9]/div/div[1]/span[1]/span/span').text,
                      ensure_ascii=False)


if __name__ == '__main__':
    app.run(port=8000)
