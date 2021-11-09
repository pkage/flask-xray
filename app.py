from flask import Flask, render_template, request, redirect, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime

import toml

app = Flask(__name__)
CONFIG_FILE = '~/.config/xray/xray.toml'

# --- HELPERS ---

def get_config_text():
    cfg = open(
        os.path.expanduser(CONFIG_FILE), 'r'
    ).read()
    return cfg

def get_config():
    return toml.loads(get_config_text())

def list_dir(directory):
    return os.listdir(directory)

def create_dirs(dirs):
    # input directory
    if not os.path.exists(dirs['input']):
        os.mkdir(dirs['input'])

    # letters directory
    if not os.path.exists(dirs['letters']):
        os.mkdir(dirs['letters'])

    # annotated directory
    if not os.path.exists(dirs['annotated']):
        os.mkdir(dirs['annotated'])

    # historical directory
    if not os.path.exists(dirs['historical']):
        os.mkdir(dirs['historical'])

def get_time():
    now = datetime.now()
    return now.strftime('%b %d %y %I:%M:%S %p')

def get_date():
    now = datetime.now()
    return now.strftime('%b %d %y')


# --- BUSINESS LOGIC ---

def process_ingest(cfg):
    for filename in os.listdir(cfg['dirs']['input']):
        new_filename = get_time() + ' - ' + filename

        shutil.move(
            os.path.join(
                cfg['dirs']['input'],
                filename
            ),
            os.path.join(
                cfg['dirs']['letters'],
                new_filename
            )
        )

def process_letters(cfg):
    for filename in os.listdir(cfg['dirs']['letters']):
        shutil.move(
            os.path.join(
                cfg['dirs']['letters'],
                filename
            ),
            os.path.join(
                cfg['dirs']['annotated'],
                filename
            )
        )

def process_historical(cfg):
    historical_folder = os.path.join(
        cfg['dirs']['historical'],
        get_date()
    )

    if not os.path.exists(historical_folder):
        os.mkdir(historical_folder)

    for filename in os.listdir(cfg['dirs']['annotated']):
        shutil.move(
            os.path.join(
                cfg['dirs']['annotated'],
                filename
            ),
            os.path.join(
                historical_folder,
                filename
            )
        )


@app.get('/')
def index():
    cfg = get_config()
    return render_template(
            'index.html',
            inputs=list_dir(cfg['dirs']['input']),
            letters=list_dir(cfg['dirs']['letters']),
            annotated=list_dir(cfg['dirs']['annotated']),
            historical=list_dir(cfg['dirs']['historical']),
            config=get_config_text(),
            render_time=get_time()
    )

@app.get('/api/ingest')
def api_ingest():
    cfg = get_config()
    process_ingest(cfg)
    return jsonify({'ok': True})

@app.get('/api/letters')
def api_letters():
    cfg = get_config()
    process_letters(cfg)
    return jsonify({'ok': True})

@app.get('/api/historical')
def api_historical():
    cfg = get_config()
    process_historical(cfg)
    return jsonify({'ok': True})


@app.get('/action/ingest')
def action_ingest():
    cfg = get_config()
    process_ingest(cfg)
    return redirect('/')

@app.get('/action/letters')
def action_letters():
    cfg = get_config()
    process_letters(cfg)
    return redirect('/')

@app.get('/action/historical')
def action_historical():
    cfg = get_config()
    process_historical(cfg)
    return redirect('/')


if __name__=='__main__':

    cfg = get_config()
    create_dirs(cfg['dirs'])


    app.run(debug=True, host='0.0.0.0', port=cfg['app']['serve_port'])
