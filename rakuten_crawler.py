# coding: utf-8

import logging,logging.handlers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

OUTDIR_SS='./file/ss/'
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

# ブラウザを起動
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)
driver.set_page_load_timeout(5)
# windowサイズを変更
win_size = driver.get_window_size()
#win_size['width']
driver.set_window_size(win_size['width'],win_size['height']+200)

# 楽天ログイン画面
log.info("getting login page")
driver.get('https://www.rakuten-card.co.jp/e-navi/')
ss(driver,1,'login')

# ログイン
log.info("logging in to the site...")
e_user = driver.find_element_by_id('u')
e_password = driver.find_element_by_id('p')
e_user.send_keys('******')
e_password.send_keys('******')
e_button = driver.find_element_by_id('loginButton')
e_button.click()
ss(driver,2,'top')




log.info("end")
exit()



# In[106]:

# ご利用明細へのリンクを探す
e_link = driver.find_element_by_xpath('//div[@class="is-fix"]/a[text()="明細を見る"]')


# In[107]:

e_link.tag_name


# In[108]:

e_link.get_attribute('href')


# In[109]:

e_link.is_displayed()


# In[110]:

# ご利用明細
e_link.click()


# In[111]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[112]:

# 確定かどうか判定
e_bill = driver.find_element_by_xpath('//div[@class="stmt-bill-info-amount__main"]/span')


# In[113]:

e_bill.text


# In[114]:

# CSVダウンロードのリンクを探す
e_csv_link = driver.find_element_by_xpath('//a[contains(.,"CSV")]')


# In[115]:

e_csv_link.get_attribute('href')


# In[116]:

e_csv_link.is_displayed()


# In[120]:

# スクロール
from selenium.webdriver.common.action_chains import ActionChains
actions = ActionChains(driver)
actions.move_to_element(e_csv_link)
actions.perform()


# In[121]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[122]:



# In[123]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[127]:

# ダウンロード可能にする
driver.command_executor._commands["send_command"] = (
    "POST",
    '/session/$sessionId/chromium/send_command'
)
params = {
    'cmd': 'Page.setDownloadBehavior',
    'params': {
        'behavior': 'allow',
        'downloadPath': '.'
    }
}
driver.execute("send_command", params=params)


# In[128]:

e_csv_link.click()


# In[129]:

driver.get_screenshot_as_file('/tmp/chrome.png')
display_png(Image('/tmp/chrome.png'))


# In[130]:

get_ipython().system('ls')


# In[133]:

# 次月が押せたら次月を押す
e_next_link = driver.find_element_by_xpath('//a[text()="次月"]')


# In[134]:

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



