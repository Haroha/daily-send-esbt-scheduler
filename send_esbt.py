#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage
import coloredlogs
import argparse
import logging
import random
import time
import sys
import re
import os

VERSION = 'ver. 20221013'  # for 20221013 ver.
URL = 'https://zh.surveymonkey.com/r/EmployeeHealthCheck'
SUBMITTED_URL = 'https://zh.surveymonkey.com/r/HCCompleted'

# Setup Timezone: 'Aisa/Taipei'
TZ = timezone(timedelta(hours=+8))

# Get system environment
load_dotenv()

logger = None

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


def ans_question(sessions, ques_num, ans_num, ans, log_str):
    time.sleep(random.randint(3, 7))
    sessions[ques_num].find_elements_by_tag_name('input')[ans_num]\
                        .send_keys(ans)
    logger.info(log_str)

def main(args):

    ID = args.id
    TEMPERATURE = 36 + (args.temp * random.randint(-2, 8) * 0.1)

    global logger
    logger = init_logger(ID, args.logdir, args.debug)

    logger.debug(args)
    logger.debug('Debug Mode: [%s].' % (args.debug))
    logger.debug('Random Temperature: [%s]. Use temperature: [%.1f]'
                    % (args.temp, TEMPERATURE))

    if args.wait:
        wait_sec = random.randint(0, 300)
        logger.info('Waiting for %d seconds.\r' % wait_sec)
        for i in range(wait_sec, 0, -1):
            sys.stdout.write('%3d' % i)
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

        sessions = browser.find_elements_by_xpath('//div[@class="question-body clearfix notranslate "]')

        # Agree
        ans_question(sessions, 0, 0, Keys.ENTER, 'Agree done.')

        # ID
        ans_question(sessions, 1, 0, ID, 'ID done.')

        # Physical Conditions
        ans_question(sessions, 2, 3, Keys.ENTER, 'Physical conditions done.')

        # Rapid test kits and result
        ans_question(sessions, 3, 3, Keys.ENTER, 'Rapid test done.')

        # Final Check
        ans_question(sessions, 5, 0, Keys.ENTER, 'Final Check done.')

        # Submit
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

        line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_TOKEN'))
        line_bot_api.broadcast(TextSendMessage('我填完體溫了唷 汪汪!'))

    except Exception as e:
        logger.error('Report failed.', exc_info=True)
        line_bot_api.broadcast(TextSendMessage('體溫填失敗了 汪汪!'))
        line_bot_api.broadcast(TextSendMessage('好像是因為這樣才錯的 汪汪!\n' + str(e)))

    finally:
        logger.info('Send ESBT done.')
        browser.quit()


if __name__ == '__main__':
    main(get_args())
