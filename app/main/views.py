from flask import render_template, send_file, make_response
from . import main

#from flask import 

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    #return make_response(open('app/templates/home.html').read())

@main.route('/busEdit.html')
def busedit():
    return render_template('server_partial/busEdit.html')

@main.route('/delstationModal.html')
def delstationModal():
    return render_template('server_partial/delstationModal.html')

@main.route('/ngtemplates/showmaproute.html')
def showmap():
    return render_template('/ngtemplates/showmaproute.html')


