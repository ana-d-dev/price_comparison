from price_comparison.db.db_access import get_all_data, get_provider_data
from price_comparison.logger_config import setup_logger
from price_comparison.utils import last_update
from flask import Flask, render_template
import time


logger = setup_logger('main')
app = Flask(__name__)
current_time = time.localtime()
date = time.strftime('%d.%m.%Y.', current_time)


@app.route('/')
def home():
    circle_images = ['a1.jpeg', 'bon-bon.png', 'tcom.jpg', 'telemach.jpeg', 'tomato.png', 'compare.webp']
    paths = ['a1', 'bon_bon', 'tcom', 'telemach', 'tomato', 'compare']
    return render_template('home.html', circle_images=circle_images, paths=paths, date=date, active_page='home')


@app.route('/a1')
def a1():
    rows = get_provider_data('A1')
    return render_template('a1.html', rows=rows, date=date, last_update=last_update(), active_page='a1')


@app.route('/bon_bon')
def bon_bon():
    rows = get_provider_data('BONBON')
    return render_template('bon_bon.html', rows=rows, date=date, last_update=last_update(), active_page='bon_bon')


@app.route('/tcom')
def tcom():
    rows = get_provider_data('T-COM')
    return render_template('tcom.html', rows=rows, date=date, last_update=last_update(), active_page='tcom')


@app.route('/telemach')
def telemach():
    rows = get_provider_data('TELEMACH')
    if rows:
        return render_template('telemach.html', rows=rows, date=date, last_update=last_update(), active_page='telemach')
    else:
        return render_template('unavailable.html', active_page='telemach')


@app.route('/tomato')
def tomato():
    rows = get_provider_data('TOMATO')
    return render_template('tomato.html', rows=rows, date=date, last_update=last_update(), active_page='tomato')


@app.route('/compare')
def compare():
    data = get_all_data()
    return render_template('compare.html', rows=data, last_update=last_update(), active_page='compare')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


if __name__ == '__main__':
    app.run(debug=True)





