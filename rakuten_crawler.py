# coding: utf-8

import logging,logging.handlers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
from argparse import ArgumentParser

OUTDIR_SS='./file/ss/'
OUTDIR='./file/'
LOGDIR='./log/'

class SeleniumHelper():
    def __init__(self, driver, ss_outdir):
        self.driver = driver
        self.ss_outdir = ss_outdir
        self.seq = 1
    def ss(self, seq=None, add_name='ss'):
        '''
        スクリーンショットを撮る
        '''
        out_seq = self.seq if seq is None else seq
        fname = '{}/{}_{}.png'.format(self.ss_outdir,out_seq,add_name)
#        log.debug("ss fname ={}".format(fname))
        driver.get_screenshot_as_file(fname)
        self.seq += 1
        return fname

#def ss(driver,seq,name=None):
#    helper = SeleniumHelper(driver, OUTDIR_SS)
#    add_name = 'ss' if name is None else name
#    fname = '{}/{}_{}.png'.format(OUTDIR_SS,seq,add_name)
#    fname = helper.ss(seq,name)
#    log.debug("ss fname ={}".format(fname))
#    driver.get_screenshot_as_file(fname)

# ログ設定
log = logging.getLogger('rakuten_crawler')
log.setLevel(logging.DEBUG)
#    h = logging.StreamHandler()
h = logging.handlers.TimedRotatingFileHandler('{}/rakuten_crawler.log'.format(LOGDIR),'D',1,13)
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

# ブラウザを起動
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)
driver.set_page_load_timeout(5)

# windowサイズを変更
win_size = driver.get_window_size()
driver.set_window_size(win_size['width']+200,win_size['height']+400)

helper = SeleniumHelper(driver, OUTDIR_SS)

# 楽天ログイン画面
log.info("getting login page")
driver.get('https://www.rakuten-card.co.jp/e-navi/')
#ss(driver,10,'login')
helper.ss(10,'login')

# ログイン
log.info("logging in to the site...")
e_user = driver.find_element_by_id('u')
e_password = driver.find_element_by_id('p')
e_user.send_keys(user_id)
e_password.send_keys(passwd)
e_button = driver.find_element_by_id('loginButton')
#ss(driver,15,'before-login')
helper.ss(15,'before-login')
e_button.click()
#ss(driver,20,'top')
helper.ss(20,'top')

# ご利用明細へのリンクを探す
log.info("navigate to bill-detail..")
#e_link = driver.find_element_by_xpath('//div[@class="is-fix"]/a[text()="明細を見る"]')
e_link = driver.find_element_by_xpath('//ul[@class="rce-u-list-plain"]//a[text()="ご利用明細"]')
log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
#ss(driver,25,'detail_link')
helper.ss(25,'detail_link')
# ご利用明細
e_link.click()
#ss(driver,30,'detail')
helper.ss(30,'detail')

# 確定かどうか判定
e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]/mark')
log.debug('bill-text:{}'.format(e_bill.text))

# CSVダウンロードのリンクを探す
log.info("downloading csv..")
e_csv_link = driver.find_element_by_xpath('//a[contains(.,"CSV")]')
log.debug('link for csv : tag={} href={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('href')))

# ダウンロード可能にする
driver.command_executor._commands["send_command"] = (
    "POST",
    '/session/$sessionId/chromium/send_command'
)
params = {
    'cmd': 'Page.setDownloadBehavior',
    'params': {
        'behavior': 'allow',
        'downloadPath': outdir
    }
}
driver.execute("send_command", params=params)

# download csv
driver.get(e_csv_link.get_attribute('href'))
#ss(driver,50,'csv_downloaded')
helper.ss(50,'csv_downloaded')

# 次月が押せたら次月を押す
log.info("navigate to next month ..")
e_next_link = driver.find_element_by_xpath('//a[text()="次月"]')
log.debug('link for next month : tag={} href={} visible={}'.format(e_next_link.tag_name, e_next_link.get_attribute('href'),e_next_link.is_displayed()))
e_next_link.click()
#ss(driver,60,'next_month')
helper.ss(60,'next_month')

# 支払い予定金額出力
log.info("write expence ..")
e_month = driver.find_element_by_xpath('//div[@class="stmt-calendar__cmd__now"]')
log.debug('month : tag={} text={}'.format(e_month.tag_name, e_month.text))
e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]')
e_mark = e_bill.find_element_by_xpath('mark')
log.debug('mark : tag={} text={}'.format(e_mark.tag_name, e_mark.text))
e_amount = e_bill.find_element_by_xpath('div[@class="stmt-bill-info-amount__num"]')
log.debug('amount : tag={} text={}'.format(e_amount.tag_name, e_amount.text))
with open('{}/{}_{}.txt'.format(outdir,e_month.text,e_mark.text), 'wt') as fout:
    fout.write(e_amount.text)

log.info("end")
exit()

