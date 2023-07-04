from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User
import re

auth = Blueprint('auth', __name__)

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        error = False
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('اکانتی با این ایمیل موجود است', category='error')
            error = True
        
        if not re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('ایمیل شما باید تنها حاوی حروف انگلیسی، عدد و یا كاراكترهاي خاص (~!$%^&*_=+}{\'?-) باشد.', category="error")
            error = True
            
        if not firstName:
            flash('لطفا نام خود را وارد كنيد!', category='error')   
            error = True
            
        if not lastName:
            flash('لطفا نام خانوادگی خود را وارد کنید!', category='error')
            error = True
            
        if not re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password1):
            flash('رمزعبور باید به طول حداقل 8 کاراکتر شامل یک حرف بزرگ، یک حرف کوچک،' 
                  'یک عدد و یک کاراکتر خاص (@$!%*?&) باشد.', category="error")
            error = True
            
        if password1 != password2:
            flash('رمزعبور به درستی تایید نشد!', category='error')
            error = True
            
        if not error:
            new_user = User(email=email, first_name=firstName, last_name=lastName, 
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            
            login_user(user, remember=True)
            
            flash('اکانت شما با موفقیت ساخته شد!', category='success')
            
            return redirect(url_for('views.home'))  # url_for('views.home') == '/'

    return render_template("signup.html", user=current_user)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('شما با موفقیت وارد شدید', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            
            flash('نام کاربری و یا رمزعبور اشتباه است', category='error')
        else:
            flash('کاربری با این نام کاربری موجود نمی باشد', category='error')
        
    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
