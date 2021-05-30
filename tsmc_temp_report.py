#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timezone, timedelta
import argparse
import time
import os
import io

URL = 'https://zh.surveymonkey.com/r/EmployeeHealthCheck'  # for 20210526 ver.
LOG = 'temp.log'

# Setup Timezone: 'Aisa/Taipei'
TZ = timezone(timedelta(hours=+8))


def get_args():
    parser = argparse.ArgumentParser(description="Photos convert to segmentation lables via CycleGAN")
    parser.add_argument("id", type=str, help="Employee ID. [%(default)s]")
    parser.add_argument("--temp", "-t", type=int,  default=36, help="Temperature. [%(default)s]")
    parser.add_argument("--wait", "-w",  type=int, default=5, help="Waiting second. [%(default)s]")
    parser.add_argument("--logfolder", "-d",  type=str, default=".", help="Log folder. [%(default)s]")
    return parser.parse_args()


class Logger(object):

    def __init__(self, ID, root):
        self.ID = ID
        self.log = os.path.join(root, "%s-%s" % (ID,LOG))
        if (not os.path.isdir(root)):
            os.makedirs(root)
        self.logfile = open(self.log, "a", buffering=1)

    def output(self, out):
        print(out)
        print(out, file=self.logfile, flush=True)

    def info(self, msg):
        out = "[%s][INFO] %s" % (datetime.now(TZ), msg)
        self.output(out)

    def ok(self, msg):
        out = "[%s][OK] \033[32m%s\033[0m" % (datetime.now(TZ), msg)
        self.output(out)

    def error(self, msg):
        out = "[%s][ERROR] \033[31m%s\033[0m" % (datetime.now(TZ), msg)
        self.output(out)

    def debug(self, msg):
        out = "[%s][DEBUG] \033[33m%s\033[0m" % (datetime.now(TZ), msg)
        self.output(out)

    def exit(self):
        self.logfile.close()


def main(args):

    ID = args.id
    TEMP = args.temp

    logger = Logger(ID, args.logfolder)

    logger.debug(args)
    logger.info("...Waiting for %d seconds." % args.wait)
    time.sleep(args.wait)

    try:

        logger.info("Start report.")
        #browser = webdriver.Remote(
        #    command_executor='http://localhost:4444/wd/hub',
        #    desired_capabilities=DesiredCapabilities.CHROME,
        #)

        op = webdriver.ChromeOptions()
        op.binary_location = os.environ.get("CHROME_BIN_PATH")
        op.add_argument("--headless")
        op.add_argument("--no-sandbox")
        op.add_argument('--disable-gpu')
        op.add_argument("--disable-dev-shm-usage")
        
        browser = webdriver.Chrome(executable_path=os.environ.get("CHROME_DRIVER_PATH"), options=op)

        browser.get( URL )
        sessions = browser.find_elements_by_xpath("//div[@class='question-body clearfix notranslate ']")

        # Session 0: Agree
        sessions[0].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info("Session 0 done.")

        # Session 1: ID
        sessions[1].find_element_by_tag_name('input').send_keys( ID )
        logger.info("Session 1 done.")

        # Session 2: Temperature Tool
        sessions[2].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info("Session 2 done.")

        # Session 3: Temperature
        sessions[3].find_element_by_tag_name('input').send_keys( TEMP )
        logger.info("Session 3 done.")

        # Session 4: Entrance Pass
        sessions[4].find_elements_by_tag_name('input')[-1].send_keys(Keys.ENTER)
        logger.info("Session 4 done.")

        # Session 5: CDC msg
        sessions[5].find_elements_by_tag_name('input')[-1].send_keys(Keys.ENTER)
        logger.info("Session 5 done.")

        # Session 6: COVID-19 Rapid Test
        sessions[6].find_elements_by_tag_name('input')[-1].send_keys(Keys.ENTER)
        logger.info("Session 6 done.")

        # Session 7: Taipei Stay
        sessions[7].find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info("Session 7 done.")

        # Session 8: Final Check
        sessions[8].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info("Session 8 done.")

        submit = browser.find_element_by_xpath("//button[@type='submit']")
        submit.send_keys(Keys.ENTER)

        logger.ok("Report successfully.")
        browser.quit()

    except Exception as e:
        logger.error("Report failed.")
        logger.error(str(e))

    logger.exit()

if __name__ == '__main__':
    main(get_args())
