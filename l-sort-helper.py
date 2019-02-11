#!/usr/bin/env python

from __future__ import print_function

import argparse, contextlib, os, sys, tempfile, shutil, datetime
import subprocess as sp

import google.auth
from googleapiclient import discovery
from google.cloud import storage

import requests

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %T")
    print('[-- {} --] {}'.format(timestamp, msg), file=sys.stderr)

# based on:
# https://stackoverflow.com/questions/3223604/how-to-create-a-temporary-directory-and-get-the-path-file-name-in-python
# http://kitchingroup.cheme.cmu.edu/blog/2013/06/16/Automatic-temporary-directory-changing/

@contextlib.contextmanager
def cd(path=None, cleanup=None):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(path))
    try:
        yield
    except Exception as err:
        raise RuntimeError(err)
    finally:
        os.chdir(prevdir)
        if cleanup: cleanup()

@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dirpath)

    with cd(path=dirpath, cleanup=cleanup):
        yield dirpath

def run(cmd):
    p = sp.Popen(
        cmd,
        shell=True,
        executable='/bin/bash',
        env=os.environ,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    p.wait()
    res = p.stdout.read().strip().decode("utf-8", "replace")
    err = p.stderr.read().strip().decode("utf-8", "replace")
    log("res: {} | err: {}".format(res, err))

    if p.returncode != 0:
        raise RuntimeError(cmd)

    return res

def download_blob(storage_client, vcf):
    bucket_name = os.path.dirname(vcf).split('/')[2]
    source_blob_name = "/".join(vcf.split('/')[3:])
    basefile = os.path.basename(vcf)
    dstpath = os.path.join(os.getcwd(), basefile)

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(dstpath)

    return dstpath

def get_input_vcfs(input_fof):
    vcfs = []
    with open(input_fof, 'r') as f:
        for line in f:
            if line.startswith('#'): continue
            vcf = line.rstrip()
            vcfs.append(vcf)
    return vcfs

def download_vcfs(storage_client, outfile, input_vcfs):
    total = len(input_vcfs)
    locally_downloaded_vcfs = []
    for (i, vcf) in enumerate(input_vcfs):
        # needed by htslib/bcftools to directly read off the bucket
        #token = get_access_token()
        #os.environ['GCS_OAUTH_TOKEN'] = token
        log("Downloading input vcf [ {} | {} ] : {}".format(i, total, vcf))
        vcfpath = download_blob(storage_client, vcf)
        log("\tDownloaded vcf to: {}".format(vcfpath))
        locally_downloaded_vcfs.append(vcfpath)

    return locally_downloaded_vcfs


def activate_google_storage_client():
    credentials, project_id = google.auth.default()
    storage_client = storage.Client(credentials=credentials, project=project_id)
    return storage_client

# see https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances#applications
def get_access_token():
    METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
    METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
    SERVICE_ACCOUNT = 'default'

    token_url = '{}instance/service-accounts/{}/token'
    token_url = token_url.format(METADATA_URL, SERVICE_ACCOUNT)

    # Request an access token from the metadata server.
    r = requests.get(token_url, headers=METADATA_HEADERS)
    r.raise_for_status()

    # Extract the access token from the response.
    access_token = r.json()['access_token']
    return access_token

def make_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", type=str, required=True,
        help="the input data to sort"
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="the sorted gvcf output file"
    )
    return parser

def main():
    parser = make_arg_parser()
    args = parser.parse_args()
    sc = activate_google_storage_client()
    input_vcfs = get_input_vcfs(args.input)
    with tempdir() as dirpath:
        vcfs = download_vcfs(sc, args.output, input_vcfs)
        # TODO: run_lsort(vcfs)

if __name__ == "__main__":
    main()
