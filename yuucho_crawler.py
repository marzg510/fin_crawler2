# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import selenium.common.exceptions

OUTDIR_SS='./file/ss_yuucho'
OUTDIR='./file/'
LOGDIR='./log/'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
h = logging.handlers.TimedRotatingFileHandler(os.path.join(LOGDIR,'%s.log' % ap_name),'D',2,13)
h.setFormatter(log_format)
log.addHandler(h)
h = logging.StreamHandler()
h.setFormatter(log_format)
log.addHandler(h)

log.info("start")

# 引数解析
usage = 'Usage: python %s USER_ID1 USER_ID2 USER_ID3 PASSWORD [--outdir <dir>] [--help]' % __file__
parser = ArgumentParser(usage=usage)
parser.add_argument('user1', type=str, help='USER ID 1')
parser.add_argument('user2', type=str, help='USER ID 2')
parser.add_argument('user3', type=str, help='USER ID 3')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user1 = args.user1
user2 = args.user2
user3 = args.user3
passwd = args.passwd
outdir = args.outdir

log.info("user_id=%s-%s-%s" % (user1,user2,user3))
log.info("outdir={}".format(outdir))

# 合言葉入力サブルーチン
def input_secret_word():
    log.info("need secret word.")
    e_q = driver.find_element_by_xpath('//dt[text()="質問"]/following-sibling::dd')
    log.debug("q=%s %s" % (e_q.tag_name,e_q.text))
    log.info("waiting word input ...")
    print(e_q.text)
    word = input('Enter Secret word :')
    e_word = driver.find_element_by_name('aikotoba')
    e_word.send_keys(word)
    e_word_link = driver.find_element_by_xpath('//a[text()="次へ"]')
    helper.ss(name='before-submit-word')
    e_word_link.click()
    helper.ss(name='after-submit-word')

# 処理開始
try:
    driver = helper.start_browser()
    helper.outdir_ss = OUTDIR_SS
    log.info("outdir_ss={}".format(helper.outdir_ss))
    helper.set_download(outdir)
    helper.is_save_html_with_ss = True

    # ログイン画面
    log.info("getting Yuucho login page")
    driver.get('https://direct.jp-bank.japanpost.jp/tp1web/U010101WAK.do?link_id=ycDctLgn')
    time.sleep(1)
    helper.ss(name='yuucho_login')

    # ログイン(お客様番号入力）
    log.info("inputting user ids for login..")
    e_user1 = driver.find_element_by_name('okyakusamaBangou1')
    e_user2 = driver.find_element_by_name('okyakusamaBangou2')
    e_user3 = driver.find_element_by_name('okyakusamaBangou3')
    e_submit = driver.find_element_by_xpath('//input[@type="button" and @name="U010103"]')
    e_user1.send_keys(user1)
    e_user2.send_keys(user2)
    e_user3.send_keys(user3)
    helper.ss(name='before-input-userID')
    e_submit.click()
    helper.ss(name='after-input-userID')

    # ログイン(合言葉)
    while '合言葉' in driver.page_source:
        input_secret_word()

    # ログイン(パスワード入力)
    log.info("inputting password for login..")
    e_password = driver.find_element_by_name('loginPassword')
    e_login = driver.find_element_by_name('U010302')
    e_password.send_keys(passwd)
    helper.ss(name='before-input-password')
    e_login.click()
    helper.ss(name='after-input-password')
    
    ############# confirm message
    if 'ゆうちょ銀行からのお知らせ' in driver.page_source:
        log.info ("confirming message")
        e_next = driver.find_element_by_xpath('//a[text()="ダイレクトトップ"]')
        e_next.click()
        helper.ss(name='yuucho-direct-top-after-confirm')

    ############# Navigate to Detail page
    log.info ("Navigate to Detail page")
    e_link = driver.find_element_by_xpath('//a[text()="入出金明細照会"]')
    log.debug('link for detail : {} {} visible={}'.format(e_link.tag_name, e_link.text,e_link.is_displayed()))
    e_link.click()
    helper.ss(name='detail')

    ############# Navigate to CSV page
    log.info ("Navigate to CSV page")
    e_term = driver.find_element_by_xpath('//label[contains(text(),"直近６か月分")]')
    log.debug('term radio : %s %s visible=%s' % (e_term.tag_name, e_term.text,e_term.is_displayed()))
    e_term.click()
    helper.ss(name='after-click-term')
    e_csv_link = driver.find_element_by_xpath('//a[@onclick and text()="データダウンロード（CSV形式）"]')
    log.debug('link for csv page : %s %s visible=%s' % (e_csv_link.tag_name, e_csv_link.get_attribute('onclick'),e_csv_link.is_displayed()))
    driver.execute_script(e_csv_link.get_attribute('onclick'))
    helper.ss(name='csv-page')

    ############# Download CSV file
    log.info ("Downloading")
    e_csv = driver.find_element_by_xpath('//a[text()="ダウンロード"]')
    log.debug('link for csv : %s %s visible=%s' % (e_csv.tag_name, e_csv.text,e_csv.is_displayed()))
    e_csv.click()
    log.info ("finish file writing to {}".format(outdir))
    helper.ss(name='after-csv-downloaded')

finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

