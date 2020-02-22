# coding: utf-8

import logging,logging.handlers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

OUTDIR_SS='./file/ss/'
OUTDIR='./file/'
LOGDIR='./log/'

def ss(driver,seq,name=None):
    '''
    スクリーンショットを撮る
    '''
    add_name = 'ss' if name is None else name
    fname = '{}/{}_{}.png'.format(OUTDIR_SS,seq,add_name)
    log.debug("ss fname ={}".format(fname))
    driver.get_screenshot_as_file(fname)


# ログ設定
log = logging.getLogger('rakuten_crawler')
log.setLevel(logging.DEBUG)
#    h = logging.StreamHandler()
h = logging.handlers.TimedRotatingFileHandler('{}/rakuten_crawler.log'.format(LOGDIR),'M',1,13)
h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
log.addHandler(h)

log.info("start")

args = sys.argv
user_id = args[1]
passwd = args[2]

# ブラウザを起動
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)
driver.set_page_load_timeout(5)


# windowサイズを変更
win_size = driver.get_window_size()
driver.set_window_size(win_size['width']+200,win_size['height']+400)

# 楽天ログイン画面
log.info("getting login page")
driver.get('https://www.rakuten-card.co.jp/e-navi/')
ss(driver,10,'login')

# ログイン
log.info("logging in to the site...")
e_user = driver.find_element_by_id('u')
e_password = driver.find_element_by_id('p')
e_user.send_keys(user_id)
e_password.send_keys(passwd)
e_button = driver.find_element_by_id('loginButton')
ss(driver,15,'before-login')
e_button.click()
ss(driver,20,'top')


# ご利用明細へのリンクを探す
log.info("navigate to bill-detail..")
#e_link = driver.find_element_by_xpath('//div[@class="is-fix"]/a[text()="明細を見る"]')
e_link = driver.find_element_by_xpath('//ul[@class="rce-u-list-plain"]//a[text()="ご利用明細"]')
log.debug('link for detail : tag={} href={} visible={}'.format(e_link.tag_name, e_link.get_attribute('href'),e_link.is_displayed()))
# スクロール
#driver.execute_script('arguments[0].scrollIntoView(true);', e_link)
ss(driver,25,'detail_link')
# ご利用明細
e_link.click()
#driver.get(e_link.get_attribute('href'))
ss(driver,30,'detail')

# 確定かどうか判定
e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]/mark')
log.debug('bill-text:{}'.format(e_bill.text))


# CSVダウンロードのリンクを探す
log.info("downloading csv..")
e_csv_link = driver.find_element_by_xpath('//a[contains(.,"CSV")]')
log.debug('link for csv : tag={} href={}'.format(e_csv_link.tag_name, e_csv_link.get_attribute('href')))

# スクロール
#from selenium.webdriver.common.action_chains import ActionChains
#actions = ActionChains(driver)
#actions.move_to_element(e_csv_link)
#actions.perform()
#driver.execute_script('arguments[0].scrollIntoView(true);', e_csv_link) 
#ss(driver,40,'csv_link')


# ダウンロード可能にする
driver.command_executor._commands["send_command"] = (
    "POST",
    '/session/$sessionId/chromium/send_command'
)
params = {
    'cmd': 'Page.setDownloadBehavior',
    'params': {
        'behavior': 'allow',
        'downloadPath': OUTDIR
    }
}
driver.execute("send_command", params=params)

# download csv
driver.get(e_csv_link.get_attribute('href'))
ss(driver,50,'csv_downloaded')

# 次月が押せたら次月を押す
log.info("navigate to next month ..")
e_next_link = driver.find_element_by_xpath('//a[text()="次月"]')
log.debug('link for next month : tag={} href={} visible={}'.format(e_next_link.tag_name, e_next_link.get_attribute('href'),e_next_link.is_displayed()))
e_next_link.click()
ss(driver,60,'next_month')

# 支払い予定金額出力
log.info("write expence ..")
e_month = driver.find_element_by_xpath('//div[@class="stmt-calendar__cmd__now"]')
log.debug('month : tag={} text={}'.format(e_month.tag_name, e_month.text))
e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]')
e_mark = e_bill.find_element_by_xpath('mark')
log.debug('mark : tag={} text={}'.format(e_mark.tag_name, e_mark.text))
e_amount = e_bill.find_element_by_xpath('div[@class="stmt-bill-info-amount__num"]')
log.debug('amount : tag={} text={}'.format(e_amount.tag_name, e_amount.text))
with open('{}/{}_{}.txt'.format(OUTDIR,e_month.text,e_mark.text), 'wt') as fout:
    fout.write(e_amount.text)


log.info("end")
exit()


# In[133]:

e_next_link.get_attribute('href')


# In[135]:

e_next_link.click()


# In[136]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[137]:

# CSVダウンロードのリンクを探す
e_csv_link = driver.find_element_by_xpath('//a[contains(.,"CSV")]')


# In[138]:

e_csv_link.get_attribute('href')


# In[139]:

e_csv_link.is_displayed()


# In[140]:

# スクロール
from selenium.webdriver.common.action_chains import ActionChains
actions = ActionChains(driver)
actions.move_to_element(e_csv_link)
actions.perform()


# In[141]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[142]:

e_csv_link.click()


# In[143]:

get_ipython().system('ls')


# In[95]:

driver.quit()


# In[ ]:



