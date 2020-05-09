# coding: utf-8

import logging,logging.handlers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys,os
from argparse import ArgumentParser
import selenium_helper as helper

OUTDIR_SS='./file/ss/'
OUTDIR='./file/'
LOGDIR='./log/'

def write_future_expence(driver, outdir):
    global log
    log.info("write furure expence to %s" % outdir)
    e_month = driver.find_element_by_xpath('//div[@class="stmt-calendar__cmd__now"]')
    log.debug('month : tag={} text={}'.format(e_month.tag_name, e_month.text))
    e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]')
    e_mark = e_bill.find_element_by_xpath('mark')
    log.debug('mark : tag={} text={}'.format(e_mark.tag_name, e_mark.text))
    e_amount = e_bill.find_element_by_xpath('div[@class="stmt-bill-info-amount__num"]')
    log.debug('amount : tag={} text={}'.format(e_amount.tag_name, e_amount.text))
    with open(os.path.join(outdir,'%s_%s.txt' % (e_month.text,e_mark.text)), 'wt') as fout:
        fout.write(e_amount.text)

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler('{}/{}.log'.format(LOGDIR,ap_name),'D',2,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)

log.info("start")

# 引数解析
usage = 'Usage: python {} USER_ID PASSWORD [--outdir <dir>] [--help]'.format(__file__)
parser = ArgumentParser(usage=usage)
parser.add_argument('user_id', type=str, help='USER ID')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user_id = args.user_id
passwd = args.passwd
outdir = args.outdir

helper.outdir_ss = OUTDIR_SS
helper.is_save_html_with_ss = True;
log.info("outdir_ss={}".format(helper.outdir_ss))

# 処理開始
try:
    # ブラウザを起動
    driver = helper.start_browser()
    driver.set_page_load_timeout(30)
    helper.set_download(outdir)

    # 楽天ログイン画面
    log.info("getting login page")
    driver.get('https://www.rakuten-card.co.jp/e-navi/')
    helper.ss(name='login')

    # ログイン
    log.info("logging in to the site...")
    e_user = driver.find_element_by_id('u')
    e_password = driver.find_element_by_id('p')
    e_user.send_keys(user_id)
    e_password.send_keys(passwd)
    e_button = driver.find_element_by_id('loginButton')
    helper.ss(name='before-login')
    e_button.click()
    helper.ss(name='top')

    # ご利用明細へのリンクを探す
    log.info("navigate to bill-detail..")
    e_link = driver.find_element_by_xpath('//ul[@class="rce-u-list-plain"]//a[text()="ご利用明細"]')
    log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
    #helper.ss(name='detail_link')
    # ご利用明細
    e_link.click()
    helper.ss(name='detail')

    # 確定かどうか判定
    #e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]/span[contains(@class,"mark")]')
    e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]/*[contains(@class,"mark")]')
    log.debug('bill-text:{}'.format(e_bill.text))

    # 未確定なら支払い予定額を保存
    if '未確定' in e_bill.text:
        write_future_expence(driver, outdir)
        log.info("end")
        exit()

    # CSVダウンロードのリンクを探す
    log.info("downloading csv..")
    e_csv_link = driver.find_element_by_xpath('//a[contains(.,"CSV")]')
    log.debug('link for csv : tag={} href={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('href')))

    # download csv
    driver.get(e_csv_link.get_attribute('href'))
    helper.ss(name='csv_downloaded')

    # 次月が押せたら次月を押す
    log.info("navigate to next month ..")
    e_next_link = driver.find_element_by_xpath('//a[text()="次月"]')
    log.debug('link for next month : tag={} href={} visible={}'.format(e_next_link.tag_name, e_next_link.get_attribute('href'),e_next_link.is_displayed()))
    e_next_link.click()
    helper.ss(name='next_month')

    # 支払い予定金額出力
    write_future_expence(driver, outdir)

finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

