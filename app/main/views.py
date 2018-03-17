from flask import render_template, send_file, make_response, request, url_for, redirect, flash
from flask_login import current_user, login_required
from ..models import mUser
from . import main

#from flask import 


@main.route('/', methods=['GET', 'POST'])
def index():
    if False == current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('index.html')
    #return make_response(open('app/templates/home.html').read())

@main.route('/infoModal.html')
def infoModal():
    return render_template('server_partial/infoModal.html')

@main.route('/ngtemplates/showmaproute.html')
def showmap():
    return render_template('/ngtemplates/showmaproute.html')
