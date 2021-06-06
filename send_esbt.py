#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timezone, timedelta
import traceback
import argparse
import random
import time
import re
import os

VERSION = 'ver. 20210604' # for 20210604 ver.
URL = 'https://zh.surveymonkey.com/r/EmployeeHealthCheck'
LOG = 'temp.log'

# Setup Timezone: 'Aisa/Taipei'
TZ = timezone(timedelta(hours=+8))


def get_args():
    parser = argparse.ArgumentParser(
        description='Auto submit Employee Self-check Body Temperature')
    parser.add_argument('id', type=str,
                        help='Employee ID. [%(default)s]')
    parser.add_argument('--temp', '-t', type=int,  default=36,
                        help='Temperature. [%(default)s]')
    parser.add_argument('--wait', '-w',  type=int, default=5,
                        help='Waiting second. [%(default)s]')
    parser.add_argument('--logfolder', '-d',  type=str, default='log/',
                        help='Log folder. [%(default)s]')
    parser.add_argument('--random', '-r', action='store_true',
                        help='Enable random temperature. [%(default)s]')
    parser.add_argument('--test', action='store_true',
                        help='Test mode. [%(default)s]')
    return parser.parse_args()


class Logger(object):

    def __init__(self, ID, root):
        self.ID = ID
        self.log = os.path.join(root, '%s-%s' % (ID, LOG))
        if not os.path.isdir(root):
            os.makedirs(root)
        self.logfile = open(self.log, 'a', buffering=1)

    def output(self, out):
        print(out)
        print(out, file=self.logfile, flush=True)

    def info(self, msg):
        out = '[%s][INFO] %s' % (datetime.now(TZ), msg)
        self.output(out)

    def ok(self, msg):
        out = '[%s][OK] \033[32m%s\033[0m' % (datetime.now(TZ), msg)
        self.output(out)

    def error(self, msg):
        out = '[%s][ERROR] \033[31m%s\033[0m' % (datetime.now(TZ), msg)
        self.output(out)

    def debug(self, msg):
        out = '[%s][DEBUG] \033[33m%s\033[0m' % (datetime.now(TZ), msg)
        self.output(out)

    def exit(self):
        self.logfile.close()


def main(args):

    ID = args.id
    TEMP = '%.1f' % (args.temp + (args.random * random.randint(-2, 6) * 0.1))

    logger = Logger(ID, args.logfolder)

    logger.debug(args)
    logger.debug('Test Mode [%s].' % (args.test))
    logger.debug('Random [%s]. Use temperature: [%s]' % (args.random, TEMP))
    logger.info('...Waiting for %d seconds.' % args.wait)
    time.sleep(args.wait)

    try:

        logger.info('Start report.')

        op = webdriver.ChromeOptions()
        op.binary_location = os.environ.get('CHROME_BIN_PATH')
        op.add_argument('--headless')
        op.add_argument('--no-sandbox')
        op.add_argument('--disable-gpu')
        op.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(
            executable_path=os.environ.get('CHROME_DRIVER_PATH'),
            options=op)

        browser.get(URL)

        title = browser.find_element(By.CLASS_NAME, 'title-text')
        version = re.search('ver\. \d+', title.text).group()
        logger.info('version: %s' % version)
        if version != VERSION:
            raise RuntimeError('Version incompatible')

        sessions = browser.find_elements_by_xpath(
            '//div[@class="question-body clearfix notranslate "]')

        # Agree
        sessions[0].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info('0 done.')

        # ID
        sessions[1].find_element_by_tag_name('input').send_keys(ID)
        logger.info('ID done.')

        # Temperature Tool
        sessions[2].find_element_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info('Temperature Tool done.')

        # Temperature
        sessions[3].find_element_by_tag_name('input').send_keys(TEMP)
        logger.info('Temperature done.')

        # High Risk Person
        sessions[4].find_elements_by_tag_name('input')[1].send_keys(Keys.ENTER)
        logger.info('High Risk Person done.')

        # Suspected Symptoms
        sessions[5].find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info('Suspected Symptoms done.')

        # COVID-19 Rapid Test
        sessions[6].find_elements_by_tag_name('input')[3].send_keys(Keys.ENTER)
        logger.info('COVID-19 Rapid Test done.')

        # Taipei Stay
        sessions[7].find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info('Taipei Stay done.')

        # Miaoli Stay
        sessions[8].find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info('Miaoli Stay done.')

        # Final Check
        sessions[9].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info('Final Check done.')

        # Submit
        submit = browser.find_element_by_xpath('//button[@type="submit"]')

        if not args.test:
            submit.send_keys(Keys.ENTER)
            logger.info('Submit done.')
        else:
            logger.info('Skip submit in test mode.')

        logger.ok('Report successfully.')
        browser.quit()

    except Exception as e:
        logger.error('Report failed.')
        traceback.print_exc()

    logger.exit()


if __name__ == '__main__':
    main(get_args())
