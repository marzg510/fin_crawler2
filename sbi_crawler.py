# coding: utf-8

import logging
import logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import datetime
from selenium.webdriver.common.by import By

thisdir = os.path.dirname(__file__)
OUTDIR_SS = os.path.join(thisdir, './file/ss_sbi')
OUTDIR = os.path.join(thisdir, './file')
LOGDIR = os.path.join(thisdir, './log')

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
h = logging.handlers.TimedRotatingFileHandler(os.path.join(LOGDIR, '%s.log' % ap_name), 'D', 2, 13)
h.setFormatter(log_format)
log.addHandler(h)
h = logging.StreamHandler(sys.stdout)
log.addHandler(h)


# 引数解析
usage = 'Usage: python %s USER_ID PASSWORD [--outdir <dir>] [--help]' % __file__
parser = ArgumentParser(usage=usage)
parser.add_argument('userid', type=str, help='USER ID 1')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()

log.info("start")
log.info("user_id=%s" % args.userid)
log.info("outdir=%s" % args.outdir)

# 処理開始
try:
    driver = helper.start_browser()
    helper.outdir_ss = OUTDIR_SS
    log.info("outdir_ss={}".format(helper.outdir_ss))
    helper.set_download(args.outdir)
    helper.is_save_html_with_ss = True
    driver.set_page_load_timeout(-1)  # max timeout

    # ログイン画面
    log.info("getting SBI login page")
    driver.get('https://www.sbisec.co.jp/ETGate')
    time.sleep(1)
    helper.ss(name='sbi_login')

    # ログイン
    log.info("inputting user ids for login..")
    e_user = driver.find_element(By.NAME, 'user_id')
    e_password = driver.find_element(By.NAME, 'user_password')
    e_submit = driver.find_element(By.XPATH, '//input[@type="image" and @name="ACT_login"]')
    e_user.send_keys(args.userid)
    e_password.send_keys(args.passwd)
    helper.ss(name='after-input-user')
    e_submit.click()
    helper.ss(name='after-click-login')

    # ############ confirm message

    # ############ Navigate to Account page
    log.info("Navigate to Account page")
    e_link = driver.find_element(By.XPATH, '//a/img[@title="口座管理"]/..')
    log.debug('link for account : %s %s visible=%s' % (e_link.tag_name, e_link.get_attribute('href'), e_link.is_displayed()))
    e_link.click()
    helper.ss(name='account')

    # ############ Navigate to Owned Securities page
    log.info("Navigate to Owned Securities")
    e_link = driver.find_element(By.XPATH, '//area[@title="保有証券"]')
    log.debug('link for owned-securities : %s %s visible=%s' % (e_link.tag_name, e_link.get_attribute('href'), e_link.is_displayed()))
    e_link.click()
    helper.ss(name='owned-securities')

    # ############ Download CSV file
    log.info("Download Owned Securities CSV")
    e_csv = driver.find_element(By.XPATH, '//a[text()="CSVダウンロード"]')
    log.debug('link for csv : %s %s visible=%s' % (e_csv.tag_name, e_csv.get_attribute('href'), e_csv.is_displayed()))
    e_csv.click()
    helper.ss(name='after-dl-owned-securities')
    # rename
    time.sleep(5)
    outfile = os.path.join(args.outdir, 'owned_security_{0:%Y%m%d_%H%M%S}.csv'.format(datetime.datetime.now()))
    os.rename(os.path.join(args.outdir, 'SaveFile.csv'), outfile)
    log.info("rename file to {}".format(outfile))

    # ############ Navigate to Total Return page
    log.info("Navigate to Total Return")
    e_link = driver.find_element(By.XPATH, '//div[@id="NAVIAREA02"]//a[text()="トータルリターン"]')
    log.debug('link for total return : %s %s visible=%s' % (e_link.tag_name, e_link.get_attribute('href'), e_link.is_displayed()))
    e_link.click()
    helper.ss(name='total-return')

    # ############ Download Total Return Summary CSV file
    log.info("Download Total Return Summary CSV")
    e_csv = driver.find_element(By.XPATH, '//div[h2[text()="サマリー"]]/following-sibling::form[@id="summaryForm"]//a[text()="CSVダウンロード"]')
    log.debug('link for total-return-summary csv : {} {} {} visible={}'.format(e_csv.tag_name, e_csv.get_attribute('href'), e_csv.text, e_csv.is_displayed()))
    e_csv.click()
    helper.ss(name='after-dl-total-return-summary')

    # ############ Download Total Return Yearly Summary CSV file
    log.info("Download Total Return Yearly Summary CSV")
    e_csv = driver.find_element(By.XPATH, '//div[h2[text()="年別サマリー"]]/following-sibling::div//a[text()="CSVダウンロード"]')
    log.debug('link for total-return-y-summary csv : {} {} {} visible={}'.format(e_csv.tag_name, e_csv.get_attribute('href'), e_csv.text, e_csv.is_displayed()))
    e_csv.click()
    helper.ss(name='after-dl-total-return-y-summary')

    # ############ Navigate to Transaction History page
    log.info("Navigate to Transaction History page")
    e_link = driver.find_element(By.XPATH, '//div[@id="NAVIAREA02"]//a[text()="取引履歴"]')
    log.debug('link for trans hist : {} {} {} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'), e_link.text, e_link.is_displayed()))
    e_link.click()
    helper.ss(name='tran-hist')

    # ############ show history
    log.info("Show Transaction History")
    e_submit = driver.find_element(By.NAME, 'ACT_search')
    e_submit.click()
    helper.ss(name='show-tran-hist')

    # ############ Download Transaction History CSV File
    log.info("Download Transaction History CSV")
    # 履歴があるかチェック
    if driver.page_source.find('指定された条件での約定履歴は見つかりませんでした') > 0:
        log.info('no transaction history csv')
    else:
        e_csv = driver.find_element(By.XPATH, '//a[text()="CSVダウンロード"]')
        log.debug('link for CSV : {} {} {} visible={}'.format(e_csv.tag_name, e_csv.get_attribute('href'), e_csv.text, e_csv.is_displayed()))
        e_csv.click()
        helper.ss(name='after-dl-tran-hist')
        time.sleep(5)
        # ダウンロードしたファイル名を取り出す
        newfile = 'SaveFile_tran_hist_{0:%Y%m%d_%H%M%S}.csv'.format(datetime.datetime.now())
        fname = helper.get_downloaded_filename(args.outdir)
        outfile = os.path.join(args.outdir, 'owned_security_{0:%Y%m%d_%H%M%S}.csv'.format(datetime.datetime.now()))
        os.rename(fname, os.path.join(args.outdir, newfile))
        log.debug('donwloaded file name = {}, rename to {}'.format(fname, newfile))

finally:
    if driver is not None:
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()
