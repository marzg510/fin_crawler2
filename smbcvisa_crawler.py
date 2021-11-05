# coding: utf-8

import logging,logging.handlers
import sys
import os
from argparse import ArgumentParser
import selenium_helper as helper
import time
import re

OUTDIR_SS='./file/ss_visa'
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

helper.outdir_ss = OUTDIR_SS
helper.is_save_html_with_ss = True;
log.info("outdir_ss={}".format(helper.outdir_ss))

# 処理開始
try:
    helper.user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko'
    driver = helper.start_browser()
    helper.set_download(outdir)
    driver.set_window_size(1920,1080)
    # SMBC VISA TOP
    log.info("getting SMBC Visa top page")
    log.debug('window size = %s' % driver.get_window_size() )
    driver.get('https://www.smbc-card.com/mem/index.jsp')
    time.sleep(10)
    page_width = driver.execute_script('return document.body.scrollWidth')
    page_height = driver.execute_script('return document.body.scrollHeight')
    log.debug('page size width=%d height=%d' % (page_width,page_height))
    driver.set_window_size(page_width, page_height)
    helper.ss(name='smbcvisa_top')
    #log.debug('cookies = {}'.format(driver.get_cookies()))
    e_user = driver.find_element_by_name('userid')
    log.debug('e_user : {} visible={}'.format(e_user.get_attribute('outerHTML'),e_user.is_displayed()))

    e_capy = driver.find_element_by_class_name('capy-captcha')
    log.debug('capy element : tag={} id={} visible={}'.format(e_capy.tag_name,e_capy.get_attribute('id'),e_capy.is_displayed()))
    capy_id = re.sub(r'capy$',"",e_capy.get_attribute('id'))
    log.info('capy id = '+capy_id)
    e_image_area = driver.find_element_by_xpath('//div[@id="'+capy_id+'image-area"]')
    e_image = e_image_area.find_element_by_name(capy_id+'image')
#    log.debug('image-area image={}'.format(e_image.get_attribute('outerHTML')))
    e_pieces = driver.find_elements_by_xpath('//div[@id="'+capy_id+'pieces"]/div')
    for i,e in enumerate(e_pieces):
#        log.debug('piece[{}] : {} visible={} location={}'.format(i, e.get_attribute('outerHTML'),e.is_displayed(),e.location))
        log.debug('piece[%d] : visible=%s location=%s outerHTML=%s' % (i, e.is_displayed(),e.location,e.get_attribute('outerHTML')))
        e_img = e.find_element_by_tag_name('img')
        import urllib.request
        urllib.request.urlretrieve(e_img.get_attribute('src'), os.path.join(helper.outdir_ss,'img_piece_%d.png' % i))
        log.debug("piece %s save to %s" % (e_img.get_attribute('src'), os.path.join(helper.outdir_ss,'img_piece_%d.png' % i)))
#    e_p = e_pieces[0]
#    e_p_img = e_p.find_element_by_name(capy_id+'image')
#    log.debug('p0 image : tag={} name={} style={} src={} visible={} location={}'.format(e_p_img.tag_name,e_p_img.get_attribute('name'),e_p_img.get_attribute('style'),e_p_img.get_attribute('src'),e_p_img.is_displayed(),e_p_img.location))
#    log.debug('p0 image : {} visible={} location={}'.format(e_p_img.get_attribute('outerHTML'),e_p_img.is_displayed(),e_p_img.location))
    #3秒間待機して移動前の位置を確認
#    time.sleep(3)
    #移動元の要素をドラッグし移動先の要素へドラッグアンドドロップ
#    actions = ActionChains(driver)
#    actions.drag_and_drop(source,target)
#    actions.perform()
finally:
    if ( driver is not None ):
        driver.quit()
        log.info("WebDriver Quit")
    log.info("end")

exit()

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
e_bill = driver.find_element_by_id('LblSumUseValue')
log.debug('future bill : tag={} text={}'.format(e_bill.tag_name, e_bill.text))
e_table = driver.find_element_by_xpath('//table[@summary="ご利用年月日。"]')
e_trs = e_table.find_elements_by_xpath('//tr')
log.debug('trs: {}'.format(e_trs))
fbill_file = '{}/請求予定の明細.txt'.format(outdir)
log.info("writeting file: {}".format(fbill_file))
with open(fbill_file, 'wt') as fout:
    fout.write('{}\n'.format(e_bill.text.strip()))
    for e_tr in e_trs:
        fout.write('{}\n'.format(e_tr.text.replace('\n',' ').replace('\r','')))

driver.close()
driver.quit()
log.info("end")
exit()

