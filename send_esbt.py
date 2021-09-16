#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timezone, timedelta
import coloredlogs
import argparse
import logging
import random
import time
import sys
import re

VERSION = 'ver. 20210721'  # for 20210721 ver.
URL = 'https://zh.surveymonkey.com/r/EmployeeHealthCheck'
SUBMITTED_URL = 'https://zh.surveymonkey.com/r/HCCompleted'

# Setup Timezone: 'Aisa/Taipei'
TZ = timezone(timedelta(hours=+8))


def get_args():

    parser = argparse.ArgumentParser(
        description='Auto submit Employee Self-check Body Temperature')
    parser.add_argument('id', type=str,
                        help='Employee ID.')
    parser.add_argument('--logdir', '-l',  type=str,
                        help='Log folder. [%(default)s]')
    parser.add_argument('--wait', '-w',  action='store_true',
                        help='Waiting random second. [%(default)s]')
    parser.add_argument('--temp', '-t', action='store_true',
                        help='Random temperature. [%(default)s]')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Debug mode. [%(default)s]')
    return parser.parse_args()


def init_logger(id, log_dir, is_debug):

    LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)8s'\
                    ' (%(module)s.%(funcName)s) %(message)s'
    LOG_LEVEL = logging.DEBUG if is_debug else logging.INFO

    if log_dir:
        # Create a filehandler object
        date_str = datetime.now().strftime('%Y%m%d')
        fh = logging.FileHandler('%s%s-%s.log' % (log_dir, id, date_str))
        fh.setLevel(LOG_LEVEL)
        fh.setFormatter(coloredlogs.ColoredFormatter(LOG_FORMAT))

        # Create a ColoredFormatter to use as formatter for the FileHandler
        logging.getLogger().addHandler(fh)

    coloredlogs.install(level=LOG_LEVEL, fmt=LOG_FORMAT)
    return logging.getLogger()


def main(args):

    ID = args.id
    TEMPERATURE = 36 + (args.temp * random.randint(-2, 8) * 0.1)

    logger = init_logger(ID, args.logdir, args.debug)

    logger.debug(args)
    logger.debug('Debug Mode: [%s].' % (args.debug))
    logger.debug('Random Temperature: [%s]. Use temperature: [%.1f]'
                    % (args.temp, TEMPERATURE))

    if args.wait:
        wait_sec = random.randint(0, 300)
        logger.info('Waiting for %d seconds.\r' % wait_sec)
        for i in range(wait_sec, 0, -1):
            sys.stdout.write(str(i))
            sys.stdout.write('\r')
            time.sleep(1)

    try:
        logger.info('Start report.')

        options = Options()
        
        if not args.debug:
            options.headless = True

        browser = webdriver.Firefox(options=options)

        browser.get(URL)

        # Check version
        title = browser.find_element(By.CLASS_NAME, 'title-text')
        version = re.search('ver\. \d+', title.text).group()
        logger.info('version: %s' % version)
        if version != VERSION:
            raise RuntimeError('Version incompatible')

        page1_sessions = browser.find_elements_by_xpath('//div[@class="question-body clearfix notranslate "]')

        # Agree
        time.sleep(random.randint(3, 7))
        page1_sessions[0].find_element_by_tag_name('input')\
                            .send_keys(Keys.ENTER)
        logger.info('Agree done.')

        # ID
        time.sleep(random.randint(3, 7))
        page1_sessions[1].find_element_by_tag_name('input')\
                            .send_keys(ID)
        logger.info('ID done.')

        # Temperature Tool
        time.sleep(random.randint(3, 7))
        page1_sessions[2].find_element_by_tag_name('input')\
                            .send_keys(Keys.ENTER)
        logger.info('Temperature Tool done.')

        # Temperature
        time.sleep(random.randint(3, 7))
        page1_sessions[3].find_element_by_tag_name('input')\
                            .send_keys(str(TEMPERATURE))
        logger.info('Temperature done.')

        # Symptoms
        time.sleep(random.randint(3, 7))
        page1_sessions[4].find_elements_by_tag_name('input')[0]\
                            .send_keys(Keys.ENTER)
        logger.info('Symptoms done.')

        # High Risk Person
        time.sleep(random.randint(3, 7))
        page1_sessions[5].find_elements_by_tag_name('input')[1]\
                            .send_keys(Keys.ENTER)
        logger.info('High Risk Person done.')

        # Got Vaccinated
        time.sleep(random.randint(3, 7))
        page1_sessions[6].find_elements_by_tag_name('input')[1]\
                            .send_keys(Keys.ENTER)
        logger.info('Got Vaccinated done.')

        # Suspected Symptoms
        time.sleep(random.randint(3, 7))
        page1_sessions[7].find_elements_by_tag_name('input')[2]\
                            .send_keys(Keys.ENTER)
        logger.info('Suspected Symptoms done.')

        # Overlap footprint
        time.sleep(random.randint(3, 7))
        page1_sessions[8].find_elements_by_tag_name('input')[3]\
                            .send_keys(Keys.ENTER)
        logger.info('Overlap footprint done.')

        # PCR nucleic acid test
        time.sleep(random.randint(3, 7))
        page1_sessions[9].find_elements_by_tag_name('input')[3]\
                            .send_keys(Keys.ENTER)
        logger.info('PCR nucleic acid test done.')

        # Rapid test result
        time.sleep(random.randint(3, 7))
        page1_sessions[10].find_elements_by_tag_name('input')[3]\
                            .send_keys(Keys.ENTER)
        logger.info('Rrapid test result done.')

        # Final Check
        time.sleep(random.randint(3, 7))
        page1_sessions[11].find_element_by_tag_name('input')\
                            .send_keys(Keys.ENTER)
        logger.info('Final Check done.')

        # Submit
        time.sleep(random.randint(3, 7))
        submit = browser.find_element_by_xpath('//button[@type="submit"]')

        if args.debug:
            logger.debug('Skip submit in test mode.')
        else:
            submit.send_keys(Keys.ENTER)
            logger.info('Submit done.')
            time.sleep(30)

            if browser.current_url != SUBMITTED_URL:
                logger.error('Browser didn\'t redirect to submitted page.')
                raise Exception

        logger.info('Report successfully.')

    except Exception:
        logger.error('Report failed.', exc_info=True)

    finally:
        logger.info('Send ESBT done.')
        browser.quit()


if __name__ == '__main__':
    main(get_args())
