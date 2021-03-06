# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import selenium.common.exceptions

OUTDIR_SS='./file/ss_view'
OUTDIR='./file/'
LOGDIR='./log/'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler('{}/{}.log'.format(LOGDIR,ap_name),'D',2,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)

log.info("start")

# 引数解析
usage = 'Usage: python {} USER_ID PASSWORD [--outdir <dir>] [--url <url>] [--help]'.format(__file__)
parser = ArgumentParser(usage=usage)
parser.add_argument('user_id', type=str, help='USER ID')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user_id = args.user_id
passwd = args.passwd
outdir = args.outdir

log.info("user_id={}".format(user_id))
log.info("outdir={}".format(outdir))
log.info("outdir_ss={}".format(helper.outdir_ss))

try:
    driver = helper.start_browser()
    helper.outdir_ss = OUTDIR_SS
    helper.set_download(outdir)

    # VIEW's NET TOP
    log.info("getting VIEW's NET top page")
    driver.get('https://www.jreast.co.jp/card/servicelist/viewsnet/login.html')
    helper.ss(name='view_top')
    #log.debug('cookies = {}'.format(driver.get_cookies()))

    # VIEW's NETのログイン画面
    log.info("getting VIEW's NET login page")
    e_login_link = driver.find_element_by_xpath('//a[contains(.,"VIEW") and contains(.,"s NETのIDで") and contains(.,"ログイン")]')
    #log.debug('login_link = tag={},href={}'.format(e_login_link.tag_name,e_login_link.get_attribute('href')))
    e_login_link.click()
    login_url = driver.current_url
    log.info('login url={}'.format(login_url))
    time.sleep(1)
    helper.ss(name='views_net_login')

    # ログイン
    log.info("logging in to the site...")
    e_user = driver.find_element_by_id('id')
    e_password = driver.find_element_by_id('pass')
    e_user.send_keys(user_id)
    e_password.send_keys(passwd)
    e_button = driver.find_element_by_xpath('//input[@type="image" and @alt="ログイン"]')
    helper.ss(name='before-login')
    e_button.click()
    helper.ss(name='view_top')


    # ご利用明細照会
    log.info("navigate to bill-detail..")
    e_link = driver.find_element_by_xpath('//a[@alt="ご利用明細照会（お支払方法の変更）"]')
    log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
    e_link.click()
    helper.ss(name='detail')

    # 確定済みの最新明細
    e_bill_link = driver.find_element_by_id('LnkClaimYm1')
    log.debug('link for bill : tag={} href={} visible={}'.format(e_bill_link.tag_name, e_bill_link.get_attribute('href'),e_bill_link.is_displayed()))
    e_bill_link.click()
    helper.ss(name='bill')

    # CSVダウンロード
    log.info("downloading csv..")
    e_csv_link = driver.find_element_by_id('BtnCsvDownloadTop')
    log.debug('link for csv : tag={} href={} visible={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('alt'),e_csv_link.is_displayed()))
    e_csv_link.click()
    helper.ss(name='csv_downloaded')

    # 請求予定の明細
    log.info("navigate to future bill ..")
    e_next_link = driver.find_element_by_id('vucV0300MonthList_LnkYotei')
    log.debug('link for next month : tag={} href={} visible={}'.format(e_next_link.tag_name, e_next_link.get_attribute('href'),e_next_link.is_displayed()))
    e_next_link.click()
    helper.ss(name='future_bill')

    # 支払い予定金額出力
    log.info("write future bill ..")
    fbill_file = '{}/請求予定の明細.txt'.format(outdir)
    log.info("writeting file: {}".format(fbill_file))
    try:
        e_mesg = driver.find_element_by_id('DivErrorMessage')
        with open(fbill_file, 'wt') as fout:
            fout.write('{}\n'.format(e_mesg.text.strip()))
        log.info('no future bill')
    except selenium.common.exceptions.NoSuchElementException:
        e_bill = driver.find_element_by_id('LblSumUseValue')
        log.debug('future bill : tag={} text={}'.format(e_bill.tag_name, e_bill.text))
        e_table = driver.find_element_by_xpath('//table[@summary="ご利用年月日。"]')
        e_trs = e_table.find_elements_by_xpath('//tr')
        log.debug('trs: {}'.format(e_trs))
        with open(fbill_file, 'wt') as fout:
            fout.write('{}\n'.format(e_bill.text.strip()))
            for e_tr in e_trs:
                fout.write('{}\n'.format(e_tr.text.replace('\n',' ').replace('\r','')))
finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

