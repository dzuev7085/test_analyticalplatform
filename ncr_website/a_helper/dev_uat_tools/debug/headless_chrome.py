# Install Chromedriver
# https://gist.github.com/ziadoz/3e8ab7e944d02fe872c3454d17af31a5
# selenium==3.13.0
from selenium import webdriver
import json
import base64
from pathlib import Path

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'  # noqa E501


LINUX_PATHS = [
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/usr/bin/chrome',
    '/usr/bin/chrome-browser',
    '/usr/local/bin/chromedriver/chromedriver',
    '/usr/local/bin/chromedriver',
]


def chrome_path():
    """Return the absolute path to Chrome"""

    for path in LINUX_PATHS:
        if Path(path).is_file():
            return path


def send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % (
        driver.session_id
    )
    url = driver.command_executor._url + resource

    body = json.dumps({'cmd': cmd, 'params': params})

    response = driver.command_executor._request('POST', url, body)

    if response['status']:
        raise Exception(response.get('value'))

    return response.get('value')


def save_as_pdf(driver, path, options={}):
    # https://timvdlippe.github.io/devtools-protocol/tot/Page#method-printToPDF

    result = send_devtools(driver, "Page.printToPDF", options)

    with open(path, 'wb') as file:
        file.write(base64.b64decode(result['data']))


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920x1080')
options.add_argument('user-agent=%s' % user_agent)

driver = webdriver.Chrome(chrome_path(),
                          chrome_options=options)

file_path = '/home/patrik/PycharmProjects/analytical_platform/analytical_platform/ncr_website/a_helper/dev_uat_tools/debug/base_template.html'  # noqa E501

driver.get("file://%s" % file_path)

save_as_pdf(driver, r'page.pdf')
