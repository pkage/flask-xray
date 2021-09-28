import requests
import sys
import time

HOST = 'http://localhost:5000'

# HELPERS

def upload_job(filename, jobname):
    files = {'jobfile': open(filename,'rb')}
    values = {'name': jobname}

    r = requests.post(HOST + '/job/new', files=files, data=values)


def check_job(jobname):
    r = requests.get(HOST + '/job/status/' + jobname)

    return r.text == 'complete'

def download_job(jobname, output):
    r = requests.get(HOST + '/job/download/' + jobname)

    open(output, 'wb').write(r.content)


# EXAMPLE

def example_job(filename, jobname):
    print(f'Uploading job {jobname}...')
    upload_job(filename, jobname)

    print(f'Polling job...')
    while not check_job(jobname):
        # sleep in seconds
        time.sleep(5)
        print(f'Polling job...')

    print(f'Downloading job...')
    download_job(jobname, 'job.zip')


if __name__=='__main__':
    example_job('requirements.txt', 'test')
