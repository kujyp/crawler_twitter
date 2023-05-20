import logging
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as elemTree
import zipfile
from io import BytesIO
from typing import Optional, AnyStr

from crawler.driver import console
from crawler.driver.configs import DEFAULT_CHROME_VERSION


def get_chromedriver_filename():
    if sys.platform.startswith('win'):
        return 'chromedriver.exe'
    return 'chromedriver'


def check_version(binary, required_version):
    try:
        version = subprocess.check_output([binary, '-v'])
        version = re.match(r'.*?([\d.]+).*?', version.decode('utf-8'))[1]
        if version == required_version:
            return True
    except Exception:
        return False
    return False


def get_linux_executable_path():
    for executable in (
        "google-chrome",
        "google-chrome-stable",
        "google-chrome-beta",
        "google-chrome-dev",
        "chromium-browser",
        "chromium",
    ):
        path = shutil.which(executable)
        if path is not None:
            return path
    return None


def get_platform_architecture():
    if sys.platform.startswith('linux') and sys.maxsize > 2 ** 32:
        platform = 'linux'
        architecture = '64'
    elif sys.platform == 'darwin':
        platform = 'mac'
        architecture = '64'
    elif sys.platform.startswith('win'):
        platform = 'win'
        architecture = '32'
    else:
        raise RuntimeError('Could not determine chromedriver download URL for this platform.')
    return platform, architecture


def get_chromedriver_url(version):
    base_url = 'https://chromedriver.storage.googleapis.com/'
    platform, architecture = get_platform_architecture()
    return base_url + version + '/chromedriver_' + platform + architecture + '.zip'


def get_chrome_version():
    platform, _ = get_platform_architecture()
    if platform == 'linux':
        path = get_linux_executable_path()
        if path is not None:
            with subprocess.Popen([path, '--version'], stdout=subprocess.PIPE) as proc:
                version = proc.stdout.read().decode('utf-8').replace('Chromium', '').replace('Google Chrome', '').strip()
        else:
            version = None
    elif platform == 'mac':
        process = subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], stdout=subprocess.PIPE)
        version = process.communicate()[0].decode('UTF-8').replace('Google Chrome', '').strip()
    elif platform == 'win':
        process = subprocess.Popen(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        )
        output = process.communicate()
        if output and output[0] and len(output[0]) > 0:
            version = output[0].decode('UTF-8').strip().split()[-1]
        else:
            process = subprocess.Popen(
                ['powershell', '-command', '$(Get-ItemProperty -Path Registry::HKEY_CURRENT_USER\\Software\\Google\\chrome\\BLBeacon).version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
            )
            version = process.communicate()[0].decode('UTF-8').strip()
    else:
        return
    return version


def get_matched_chromedriver_version(version):
    doc = urllib.request.urlopen('https://chromedriver.storage.googleapis.com').read()
    root = elemTree.fromstring(doc)
    for k in root.iter('{http://doc.s3.amazonaws.com/2006-03-01}Key'):
        if k.text.find(get_major_version(version) + '.') == 0:
            return k.text.split('/')[0]
    return


def get_major_version(version):
    return version.split('.')[0]


def download_chromedriver(path: Optional[AnyStr] = None):
    chrome_version = get_chrome_version()
    if not chrome_version:
        console.info('Chrome is not installed.')
        chrome_version = DEFAULT_CHROME_VERSION
    chromedriver_version = get_matched_chromedriver_version(chrome_version)
    if not chromedriver_version:
        logging.warning('Can not find chromedriver for currently installed chrome version.')
        return
    major_version = get_major_version(chromedriver_version)

    if path:
        if not os.path.isdir(path):
            raise ValueError(f'Invalid path: {path}')
        chromedriver_dir = os.path.join(
            os.path.abspath(path),
            major_version
        )
    else:
        chromedriver_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            major_version
        )
    chromedriver_filename = get_chromedriver_filename()
    chromedriver_filepath = os.path.join(chromedriver_dir, chromedriver_filename)
    if not os.path.isfile(chromedriver_filepath) or \
            not check_version(chromedriver_filepath, chromedriver_version):
        logging.info(f'Downloading chromedriver ({chromedriver_version})...')
        if not os.path.isdir(chromedriver_dir):
            os.makedirs(chromedriver_dir)
        url = get_chromedriver_url(chromedriver_version)
        try:
            response = urllib.request.urlopen(url)
            if response.getcode() != 200:
                raise urllib.error.URLError('Not Found')
        except urllib.error.URLError:
            raise RuntimeError(f'Failed to download chromedriver archive: {url}')
        archive = BytesIO(response.read())
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extract(chromedriver_filename, chromedriver_dir)
    else:
        logging.info('Chromedriver is already installed.')
    if not os.access(chromedriver_filepath, os.X_OK):
        os.chmod(chromedriver_filepath, 0o744)
    return chromedriver_filepath
