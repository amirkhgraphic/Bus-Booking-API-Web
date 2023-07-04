from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from typing import Final
import requests
import json
import re

views = Blueprint('views', __name__)

BASE_URL: Final = 'http://127.0.0.1:5000'

farsi_int = {'۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
             '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'}

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    data = dict()
    
    if request.method == 'POST':
        src = request.form.get('src')
        dst = request.form.get('dst')
        date = request.form.get('date')
        error = False
        
        if not src:
            flash('لطفا مبدا را وارد کنید!', category='error')
            error = True
        if not dst:
            flash('لطفا مقصد را وارد کنید!', category='error')
            error = True
        if not re.match("\d{4} \d{1,2} \d{1,2}$", date):
            flash('لطفا تاریخ را به صورت (سال ماه روز) وارد کنید! نمونه: 1402 4 12', category='error')
            error = True

        if not error:
            response_src = requests.get(f"{BASE_URL}/f_translate/?info={src}")
            translate_src = response_src.json()

            response_dst = requests.get(f"{BASE_URL}/f_translate/?info={dst}")
            translate_dst = response_dst.json()

            response = requests.get(f"{BASE_URL}/ticket/?info={translate_src}/"
                                    f"{translate_dst}/{date}").json()
            print(response)
            
            tickets = list()
            
            for value in response.values():
                value["empty_seats"] = int(''.join(farsi_int[i] if i in farsi_int else i for i in value["empty_seats"]))
                if value["empty_seats"] != 0:
                    ticket = dict()
                    ticket['src'] = src
                    ticket['dst'] = dst
                    ticket['date'] = date
                    ticket["com"] = value['company_name']
                    ticket["seats"] = value['empty_seats']
                    ticket["price"] = f"{''.join(farsi_int[i] if i in farsi_int else i for i in value['price'].split()[2])} ریال"
                    ticket["time"] = ''.join(farsi_int[i] if i in farsi_int else i for i in value["departure_time"][0])                
                    
                    tickets.append(ticket)
            
            data['response'] = tickets
            
            return redirect(url_for('views.tickets', data=json.dumps(data)))

    return render_template('home.html', user=current_user)

@views.route('/tickets', methods=['GET', 'POST'])
@login_required
def tickets():
    data = request.args.get('data')
    data = json.loads(data)
    print(data)
    if request.method == 'POST':
        data = data['response']
        idx = int(request.form.get('index'))
        
        data = data[idx]
        
        return redirect(url_for('views.result', data=json.dumps(data)))
    
    return render_template('tickets.html', data=data, user=current_user)

@views.route('/result')
@login_required
def result():
    data = request.args.get('data')
    data = json.loads(data)
    
    response_dst = requests.get(f"{BASE_URL}/f_translate/?info={data['dst']}")
    translate_dst = response_dst.json()

    response = requests.get(f"{BASE_URL}/weather/?info={translate_dst}")
    weather = response.json()
    
    response_wearher = requests.get(f"{BASE_URL}/e_translate/?info={weather['weather_circumstance']}")
    translate_weather = response_wearher.json()
    
    return render_template('result.html', data=data, weather=weather, translate_weather=translate_weather, user=current_user)
    