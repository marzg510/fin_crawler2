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
usage = 'Usage: python {} USER_ID PASSWORD [--outdir <dir>] [--help]'.format(__file__)
parser = ArgumentParser(usage=usage)
parser.add_argument('user_id', type=str, help='USER ID')
parser.add_argument('passwd', type=str, help='PASSWORD')
parser.add_argument('-o', '--outdir', type=str, help='file output directory', default=OUTDIR)
args = parser.parse_args()
user_id = args.user_id
passwd = args.passwd
outdir = args.outdir

# 処理開始
try:
    helper.user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko'
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
    url = 'https://www.aeon.co.jp/NetBranch/view.do'
    log.info("login page url="+url)
    driver.get(url)
    helper.ss(name='aeon_login')
    login_url = driver.current_url
    log.info('login url={}'.format(login_url))

    # ログイン
    log.info("logging in to the site...")
    e_user = driver.find_element_by_name('netMemberId')
    e_password = driver.find_element_by_name('password')
    e_user.send_keys(user_id)
    e_password.send_keys(passwd)
    e_button = driver.find_element_by_xpath('//button[@type="submit"]')
    helper.ss(name='aeon_before-login')
    e_button.click()
    helper.ss(name='aeon_top')

    # ワンタイムパスワード
    if '普段と異なる環境からのアクセスと判断されました。' in driver.page_source:
        log.info("need one time password.")
        # ワンタイムパスワード送信
        e_mail_address = driver.find_element_by_class_name('mailaddress')
        log.info('mail = {}'.format(e_mail_address.text))
        e_send_link = driver.find_element_by_xpath('//a[text()="ワンタイムパスワード送信"]')
        log.debug('send_mail_link = {} {}'.format(e_send_link.tag_name,e_send_link.get_attribute('href')))
        e_send_link.click()
        helper.ss(name='ontime_passwd_sended')
    #    helper.ps(name='ontime_passwd_sended')
        # ワンタイムパスワード入力
        log.info("waiting OTP input ...")
        otp = input('Enter One Time Password :')
    #    print('otp={}'.format(otp))
        e_otp = driver.find_element_by_name('otpwd')
        e_terminal = driver.find_element_by_name('registName')
    #    log.debug('otp = {} {} visible={}'.format(e_otp.tag_name,e_otp.get_attribute('name'),e_otp.is_displayed()))
        e_otp.send_keys(otp)
        e_terminal.send_keys(TERMINAL_NAME)
        helper.ss(name='input_otp')
        time.sleep(3)
        e_accept_link = driver.find_element_by_xpath('//a[text()="認証する"]')
        log.debug('accept_link = {} {} visible={}'.format(e_accept_link.tag_name,e_accept_link.get_attribute('href'),e_accept_link.is_displayed()))
        e_accept_link.click()
        helper.ss(name='otp_accepted')
        if ( '追加認証完了' in driver.find_element_by_tag_name('title').text ):
            print('OTP accepted!')
            log.info('One TIme Password OK, body text is below')
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



    # ご利用明細へ
    log.info("navigate to bill-detail..")
    # iframe読み込み
    iframe = driver.find_element_by_xpath('//iframe[@id="mypage_card"]')
    driver.switch_to.frame(iframe)
    e_link = driver.find_element_by_xpath('//a[text()="ご利用明細照会"]')
    log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
    e_link.click()
    helper.ss(name='detail')

    # CSVダウンロード
    log.info("downloading csv..")
    e_csv_links = driver.find_elements_by_xpath('//a[text()="今月分(CSV形式)のダウンロード"]')
    if len(e_csv_links) > 0:
        e_csv_link = e_csv_links[0]
        log.debug('link for csv : tag={} href={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('href')))
        e_csv_link.click()
        helper.ss(name='csv_downloaded')
    else:
        log.info("no csv links, can't download csv.")

    # 最近の請求金額へ
    log.info("navigate to latest bill ..")
    e_latest_link = driver.find_element_by_xpath('//a[text()="最近"]')
    log.debug('link for latest : tag={} href={} visible={}'.format(e_latest_link.tag_name, e_latest_link.get_attribute('href'),e_latest_link.is_displayed()))
    e_latest_link.click()
    helper.ss(name='latest_month')

    # 支払い予定金額出力
    log.info("write latest bill ..")
    e_latest_bill = driver.find_element_by_class_name('Sharedpart_contents-main')
    with open(os.path.join(outdir,'最近のご利用明細.txt'), 'wt') as out:
        for l in e_latest_bill.text.splitlines():
            log.debug(l)
            out.write(l+'\n')

finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()
