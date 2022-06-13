# coding: utf-8

import logging,logging.handlers
import sys,os,time
from argparse import ArgumentParser
import selenium_helper as helper

OUTDIR_SS='./file/ss_aeon'
OUTDIR='./file/'
LOGDIR='./log/'
TERMINAL_NAME = 'クローラーＰＹ'

# ログ設定
ap_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(ap_name)
log.setLevel(logging.DEBUG)
h = logging.handlers.TimedRotatingFileHandler('{}/{}.log'.format(LOGDIR,ap_name),'D',2,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)

log.info("start")

# 引数解析
usage = 'Usage: python {} USER_ID PASSWORD DUE_MON DUE_YEAR CVC [--outdir <dir>] [--help]'.format(__file__)
parser = ArgumentParser(usage=usage)
parser.add_argument('user_id', type=str, help='USER ID')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('due_mon', type=str, help='DUE MONTH')
parser.add_argument('due_year', type=str, help='DUE YEAR')
parser.add_argument('cvc', type=str, help='CVC')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user_id = args.user_id
passwd = args.passwd
outdir = args.outdir
driver = None

# 処理開始
try:
#    helper.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    helper.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    driver = helper.start_browser()
    helper.outdir_ss = OUTDIR_SS
    helper.set_download(outdir)
    helper.is_save_html_with_ss = True
    driver.set_page_load_timeout(-1) # max timeout

    # AEON TOP
    log.info("getting AEON top page")
    driver.get('https://www.aeon.co.jp/')
    helper.ss(name='aeon_top')

    # ログイン画面
    log.info("getting login page")
    url = 'https://www.aeon.co.jp/app/'
    log.info("login page url="+url)
    driver.get(url)
    helper.ss(name='aeon_login')
    login_url = driver.current_url
    log.info('login url={}'.format(login_url))

    # ログイン
    log.info("logging in to the site...")
    time.sleep(5)
#    e_user = driver.find_element_by_name('netMemberId')
    e_user = driver.find_element_by_id('username')
#    e_password = driver.find_element_by_name('password')
    e_password = driver.find_element_by_id('password')
    e_user.send_keys(user_id)
    e_password.send_keys(passwd)
    e_button = driver.find_element_by_xpath('//button[@type="submit"]')
    helper.ss(name='aeon_before-login')
    e_button.click()
    time.sleep(5)
    helper.ss(name='aeon_top')

    # ワンタイムパスワード
    if '普段と異なる環境からのアクセスと判断されました。' in driver.page_source:
        log.info("need one time password.")
        # ワンタイムパスワード送信
        e_send_btn = driver.find_element_by_xpath('//span[text()="送信"]/..')
        log.info('btn = {} {}'.format(e_send_btn.tag_name,e_send_btn.text))
#        e_send_link = driver.find_element_by_xpath('//a[text()="ワンタイムパスワード送信"]')
#        log.debug('send_mail_link = {} {}'.format(e_send_link.tag_name,e_send_link.get_attribute('href')))
        e_send_btn.click()
        helper.ss(name='ontime_passwd_sended')
        # ワンタイムパスワード入力
        log.info("waiting OTP input ...")
        otp = input('Enter One Time Password :')
    #    print('otp={}'.format(otp))
        e_otp = driver.find_element_by_id('oneTimePassword')
        e_otp.send_keys(otp)
        e_add_term = driver.find_element_by_id('addTerminal1')
        e_add_term.click()
        e_terminal = driver.find_element_by_name('newTerminalName')
    #    log.debug('otp = {} {} visible={}'.format(e_otp.tag_name,e_otp.get_attribute('name'),e_otp.is_displayed()))
        e_terminal.send_keys(TERMINAL_NAME)
        helper.ss(name='input_otp')
        time.sleep(3)
        e_accept_link = driver.find_element_by_id('btn_riskbased_otp_submit')
        log.debug('accept_link = {} {} visible={}'.format(e_accept_link.tag_name,e_accept_link.get_attribute('href'),e_accept_link.is_displayed()))
        e_accept_link.click()
        helper.ss(name='otp_accepted')
        if ( '追加認証完了' in driver.find_element_by_tag_name('title').text ):
            print('OTP accepted!')
            log.info('One Time Password OK, body text is below')
            for l in driver.find_element_by_tag_name('body').text.splitlines():
                log.info(l)
            e_mypage_link = driver.find_element_by_xpath('//a[text()="MyPageへ"]')
            log.debug('mypage_link = {} {} visible={}'.format(e_mypage_link.tag_name,e_mypage_link.get_attribute('href'),e_mypage_link.is_displayed()))
            e_mypage_link.click()

    elif 'システムからのお知らせ' in driver.page_source:
        log.error("!!! SYSTEM INFORMATION DETECTED !!!")
        log.error("body text is below")
        for l in driver.find_element_by_tag_name('body').text.splitlines():
            log.error(l)
        log.error("error end")
        sys.exit(9)

    # 最近のご利用金額
    log.info("getting latest bill..")
    e_latest_bill = driver.find_element_by_xpath('//div[@class="m-mtphistorypanel_billing"]')
    # 支払い予定金額出力
    log.info("write latest bill ..")
    with open(os.path.join(outdir,'最近のご利用明細.txt'), 'wt') as out:
        for l in e_latest_bill.text.splitlines():
            log.debug(l)
            out.write(l+'\n')

    # ご利用明細へ
    log.info("navigate to bill-detail..")
    e_link = driver.find_element_by_xpath('//a[@class="m-mtpusagepanel_infomationcontainer"]')
    log.debug('link for bill : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
    e_link.click()
    time.sleep(3)
    helper.ss(name='detail')

    # 明細書ダウンロード
    log.info("navigate to detail DL page ..")
    e_link = driver.find_element_by_xpath('//*[@id="react-tabs-5"]//a[.="明細書ダウンロード"]')
    log.debug('link for detail page : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
    e_link.click()
    time.sleep(3)
    helper.ss(name='detailpage')

    # ご本人様の確認
    if 'ご本人さまの確認が必要です' in driver.page_source:
#        log.info("waiting DUE Month input ...")
#        due_mon = input('Enter Due Month(2char) :')
#        log.info("waiting DUE Year input ...")
#        due_year = input('Enter Due Year(2char) :')
#        log.info("waiting CVC input ...")
#        cvc = input('Enter CVC (3char) :')
        e_due_mon = driver.find_element_by_name('expiration_month')
        e_due_mon.send_keys(args.due_mon)
        e_due_year = driver.find_element_by_name('expiration_year')
        e_due_year.send_keys(args.due_year)
        e_cvc = driver.find_element_by_name('securityCode')
        e_cvc.send_keys(args.cvc)
        e_accept = driver.find_element_by_xpath('//button[@type="submit" and .="認証"]')
        helper.ss(name='before_identify')
        e_accept.click()
        time.sleep(3)
        helper.ss(name='after_identify')

    # CSVダウンロード
    log.info("downloading csv..")
#    e_csv_radio = driver.find_element_by_xpath('//input[@type="radio" and .="CSV"]')
    e_csv_radio = driver.find_element_by_xpath('//div[@class="a-radio_body" and .="CSV"]')
#    e_csv_radio.set_value(2)
    e_csv_radio.click()
    e_csv_link = driver.find_element_by_xpath('//button[@type="submit" and .="ダウンロード"]')
    log.debug('link for csv : tag={} href={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('href')))
    helper.ss(name='before_download')
    e_csv_link.click()
    time.sleep(5)
    helper.ss(name='csv_downloaded')

    # 最近の請求金額へ
#    log.info("navigate to latest bill ..")
#    e_latest_link = driver.find_element_by_xpath('//a[text()="最近"]')
#    log.debug('link for latest : tag={} href={} visible={}'.format(e_latest_link.tag_name, e_latest_link.get_attribute('href'),e_latest_link.is_displayed()))
#    e_latest_link.click()
#    helper.ss(name='latest_month')


except Exception as e:
    log.exception('exception occurred.')
    print(e, file=sys.stderr)
#    import traceback
#    traceback.print_exc(file=sys.stderr)

finally:
    if (driver is not None):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()
