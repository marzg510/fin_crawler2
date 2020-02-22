# coding: utf-8

class SeleniumHelper():
    def __init__(self, driver, ss_outdir):
        self.driver = driver
        self.ss_outdir = ss_outdir
        self.seq = 1
    def ss(self, seq=None, name='ss'):
        '''
        スクリーンショットを撮る
        '''
        out_seq = self.seq if seq is None else seq
        fname = '{}/{}_{}.png'.format(self.ss_outdir,out_seq,name)
#        log.debug("ss fname ={}".format(fname))
        self.driver.get_screenshot_as_file(fname)
        self.seq += 1
        return fname

if __name__ == '__main__':
    pass
#    helper = SeleniumHelper()

