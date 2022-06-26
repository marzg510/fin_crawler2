# coding: utf-8

import logging
import logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import selenium.common.exceptions
from selenium.webdriver.common.by import By

OUTDIR_SS = './file/ss_smbc'
OUTDIR = './file/'
LOGDIR = './log/'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler('{}/{}.log'.format(LOGDIR, ap_name), 'D', 2, 13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)

log.info("start")

# 引数解析
usage = 'Usage: python {} USER_ID1 USER_ID2 PASSWORD ACCOUNT_NO [--outdir <dir>] [--url <url>] [--help]'.format(__file__)
parser = ArgumentParser(usage=usage)
parser.add_argument('user1', type=str, help='USER ID 1')
parser.add_argument('user2', type=str, help='USER ID 2')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('account', type=str, help='ACCOUNT_NO')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user1 = args.user1
user2 = args.user2
passwd = args.passwd
account = args.account
outdir = args.outdir

log.info("user_id={} {}".format(user1, user2))
log.info("account={}".format(account))
log.info("outdir={}".format(outdir))

outfile = os.path.join(outdir, 'smbc_{}_{}.csv'.format(account, time.strftime('%Y%m%d', time.localtime())))
log.info("outfile=%s" % outfile)

# 処理開始
try:
    driver = helper.start_browser()
    helper.outdir_ss = os.path.join(OUTDIR_SS, account)
    log.info("outdir_ss={}".format(helper.outdir_ss))
    helper.set_download(outdir)
    helper.is_save_html_with_ss = True
    driver.set_page_load_timeout(60)

    # ログイン画面
    log.info("getting SMBC login page")
    driver.get('https://direct.smbc.co.jp/aib/aibgsjsw5001.jsp')
    time.sleep(1)
    helper.ss(name='smbc_login')

    # ############# system maintainance check
    try:
        e_sorry = driver.find_element(By.CSS_SELECTOR, 'div#sorry')
        log.error("システムメンテナンス中")
        log.error("error end")
        sys.exit(9)
    except selenium.common.exceptions.NoSuchElementException:
        pass

    # ログイン
    log.info("logging in to the site...")

    e_tab = driver.find_element(By.ID, 'tab-switchB02')
    e_tab.click()
    time.sleep(1)
    helper.ss(name='smbc_login_tab_clicked')

    e_user1 = driver.find_element(By.NAME, 'userId1')
    e_user2 = driver.find_element(By.NAME, 'userId2')
    e_password = driver.find_element(By.ID, 'inputpassword')
    e_user1.send_keys(user1)
    e_user2.send_keys(user2)
    e_password.send_keys(passwd)
    helper.ss(name='before-login')
    e_submit = driver.find_element(By.XPATH, "//div[@class='btn-wrap']/a[.='ログイン']")
    e_submit.click()
    time.sleep(3)
    helper.ss(name='after-login')

    # ############ login check
    e_errs = driver.find_elements(By.XPATH, "//dt[@class='title' and contains(text(),'エラーコード')]")
    if len(e_errs) > 0:
        log.error("login failure")
        for err in e_errs:
            log.error(err)
        raise Exception('login failure')

    # ############ confirm message
    log.info("confirming message")
    e_next = driver.find_elements(By.XPATH, '//span[text()="確認して次へ"]/..')
    if e_next:
        e_next[0].click()
    else:
        log.info("no messages to confirm")
    helper.ss(name='smbc-top-after-confirm')

    # ############ Navigate to Detail page
    log.info("Navigate to Detail page")
    e_link = driver.find_element(By.XPATH, "//a[contains(@onclick,'{}')]".format(account))
    log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'), e_link.is_displayed()))
    e_link.click()
    time.sleep(1)
    helper.ss(name='detail')

    # ############ Download CSV file
    log.info("Downloading")
    e_csv = driver.find_element(By.XPATH, "//a[contains(.,'明細をCSVダウンロード')]")
    log.debug('link for csv : tag={} href={} visible={}'.format(e_csv.tag_name, e_csv.get_attribute('href'),e_csv.is_displayed()))
    e_csv.click()
    log.info("finish file writing to {}".format(outdir))
    helper.ss(name='after-csv-downloaded')

    # rename
    time.sleep(30)
    os.rename(os.path.join(outdir, 'meisai.csv'), outfile)
    log.info("rename file to {}".format(outfile))

except Exception as e:
    log.exception('exception occurred.')
    print(e, file=sys.stderr)

finally:
    if (driver is not None):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

