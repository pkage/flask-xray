from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)
JOBS_DIR = './jobs'
DONE_DIR = './done'

# --- EXTEND HERE ---

def start_job(job_dir, job_file):
    # TODO: start your job
    # subprocess is a tool for this
    import subprocess
    subprocess.run(['echo', 'Hello from the job file'])

# we'll need some way for checking that jobs are complete
def check_job_complete(job_name):
    return os.path.exists(
        os.path.join(JOBS_DIR, job_name, 'done.txt')
    )


# --- HELPERS ---


# Some setup: we'll need to know how many folders are in the jobs folder
def get_all_jobs():
    return os.listdir(JOBS_DIR)


# create a new folder for a job
def create_job_dir(job_name):
    directory = os.path.join(JOBS_DIR, job_name)
    os.mkdir(directory)
    return directory


# zip up a job folder when it's done
def zip_job_folder(job_name):
    # locate the folder
    job_dir = os.path.join(JOBS_DIR, job_name)

    # figure out where we'll save it
    output_filename = os.path.join(DONE_DIR, job_name)

    # check if we've already done it, if so don't redo work
    if not os.path.exists(output_filename + '.zip'):
        # make the zip file
        shutil.make_archive(output_filename, 'zip', job_dir)

    return output_filename + '.zip'



# A quick function to make sure the folders exist
# if they do, nothing happens
# if they don't, they're created
def folder_setup():
    if not os.path.exists(JOBS_DIR):
        os.mkdir(JOBS_DIR)
    if not os.path.exists(DONE_DIR):
        os.mkdir(DONE_DIR)


# --- WEB SERVER ---

# Here, we'll implement our index page
# This will show all the jobs we're currently keeping track of
# and their completion status
@app.route('/')
def index():
    folder_setup()

    jobs = []
    for job in get_all_jobs():
        job_obj = {
            'name': job,
            'complete': check_job_complete(job) # shorthand, is True or False
        }
        jobs.append(job_obj)

    return render_template(
        'index.html',
        jobs=jobs
    )


# Create a new job
@app.route('/job/new', methods=['POST'])
def upload_job():
    # get the job name from the request
    job_name = request.form['name']
    job_name = secure_filename(job_name)

    # initialize the directory
    job_dir = create_job_dir(job_name)

    # get the file (there should be only one)
    jobfile = request.files['jobfile']
    filename = secure_filename(jobfile.filename)

    # save to the directory
    jobfile.save(os.path.join(job_dir, filename))

    # kick off the job
    start_job(job_dir, filename)

    return redirect('/')

@app.route('/job/download/<job_name>')
def download_job(job_name):
    # zip up job folder
    zipname = zip_job_folder(job_name)

    return send_file(zipname, mimetype='application/zip')

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')
