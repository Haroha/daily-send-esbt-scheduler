#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import timezone, timedelta
import traceback
import argparse
import random
import time
import re
import os

VERSION = 'ver. 20210721'  # for 20210709 ver.
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
        out = '[INFO] %s' % msg
        self.output(out)

    def ok(self, msg):
        out = '[OK] \033[32m%s\033[0m' % msg
        self.output(out)

    def error(self, msg):
        out = '[ERROR] \033[31m%s\033[0m' % msg
        self.output(out)

    def debug(self, msg):
        out = '[DEBUG] \033[33m%s\033[0m' % msg
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
    if not args.test:
        logger.info('...Waiting for %d seconds.' % args.wait)
        time.sleep(args.wait)

    try:

        logger.info('Start report.')

        options = Options()
        options.headless = True

        browser = webdriver.Firefox(options=options)

        browser.get(URL)

        title = browser.find_element(By.CLASS_NAME, 'title-text')
        version = re.search('ver\. \d+', title.text).group()
        logger.info('version: %s' % version)
        if version != VERSION:
            raise RuntimeError('Version incompatible')

        page1_sessions = browser.find_elements_by_xpath(
            '//div[@class="question-body clearfix notranslate "]')

        # Agree
        time.sleep(random.randint(3, 7))
        page1_sessions[0].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info('Agree done.')

        # ID
        time.sleep(random.randint(3, 7))
        page1_sessions[1].find_element_by_tag_name('input').send_keys(ID)
        logger.info('ID done.')

        # Temperature Tool
        time.sleep(random.randint(3, 7))
        page1_sessions[2].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info('Temperature Tool done.')

        # Temperature
        time.sleep(random.randint(3, 7))
        page1_sessions[3].find_element_by_tag_name('input').send_keys(TEMP)
        logger.info('Temperature done.')

        # Symptoms
        time.sleep(random.randint(3, 7))
        page1_sessions[4].find_elements_by_tag_name('input')[0].send_keys(Keys.ENTER)
        logger.info('Symptoms done.')

        # High Risk Person
        time.sleep(random.randint(3, 7))
        page1_sessions[5].find_elements_by_tag_name('input')[1].send_keys(Keys.ENTER)
        logger.info('High Risk Person done.')

        # Got Vaccinated
        time.sleep(random.randint(3, 7))
        page1_sessions[6].find_elements_by_tag_name('input')[1].send_keys(Keys.ENTER)
        logger.info('Got Vaccinated done.')

        # Suspected Symptoms
        time.sleep(random.randint(3, 7))
        page1_sessions[7].find_elements_by_tag_name('input')[2].send_keys(Keys.ENTER)
        logger.info('Suspected Symptoms done.')

        # Overlap footprint
        time.sleep(random.randint(3, 7))
        page1_sessions[8].find_elements_by_tag_name('input')[3].send_keys(Keys.ENTER)
        logger.info('Overlap footprint done.')

        # PCR nucleic acid test
        time.sleep(random.randint(3, 7))
        page1_sessions[9].find_elements_by_tag_name('input')[3].send_keys(Keys.ENTER)
        logger.info('PCR nucleic acid test done.')

        # Rapid test result
        time.sleep(random.randint(3, 7))
        page1_sessions[10].find_elements_by_tag_name('input')[3].send_keys(Keys.ENTER)
        logger.info('Rrapid test result done.')

        # Final Check
        time.sleep(random.randint(3, 7))
        page1_sessions[11].find_element_by_tag_name('input').send_keys(Keys.ENTER)
        logger.info('Final Check done.')

        # Submit
        time.sleep(random.randint(3, 7))
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
