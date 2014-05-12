# coding: utf-8
from unittest import TestCase
import json
import os

from grab import Grab, GrabMisuseError
from .tornado_util import SERVER
from .util import TMP_FILE, TMP_DIR, GRAB_TRANSPORT, clear_directory
from grab.base import reset_request_counter

class TestCookies(TestCase):
    def setUp(self):
        SERVER.reset()

    def test_log_option(self):
        clear_directory(TMP_DIR)
        reset_request_counter()

        log_file_path = os.path.join(TMP_DIR, 'log.html')
        g = Grab(transport=GRAB_TRANSPORT)
        g.setup(log_file=log_file_path)
        SERVER.RESPONSE['get'] = 'omsk'

        self.assertEqual(os.listdir(TMP_DIR), [])
        g.go(SERVER.BASE_URL)
        self.assertEqual(os.listdir(TMP_DIR), ['log.html'])
        self.assertEqual(open(log_file_path).read(), 'omsk')


    def test_log_dir_option(self):
        clear_directory(TMP_DIR)
        reset_request_counter()

        g = Grab(transport=GRAB_TRANSPORT)
        g.setup(log_dir=TMP_DIR)
        SERVER.RESPONSE_ONCE['get'] = 'omsk1'
        SERVER.RESPONSE['get'] = 'omsk2'

        self.assertEqual(os.listdir(TMP_DIR), [])
        g.go(SERVER.BASE_URL)
        g.go(SERVER.BASE_URL)
        self.assertEqual(sorted(os.listdir(TMP_DIR)), ['01.html', '01.log', '02.html', '02.log'])
        self.assertEqual(open(os.path.join(TMP_DIR, '01.html')).read(), 'omsk1')
        self.assertEqual(open(os.path.join(TMP_DIR, '02.html')).read(), 'omsk2')

    def test_log_dir_response_content(self):
        clear_directory(TMP_DIR)
        reset_request_counter()

        g = Grab(transport=GRAB_TRANSPORT)
        g.setup(log_dir=TMP_DIR)
        SERVER.RESPONSE['get'] = 'omsk'
        SERVER.RESPONSE['headers'] = [('X-Engine', 'PHP')]

        self.assertEqual(os.listdir(TMP_DIR), [])
        g.go(SERVER.BASE_URL)
        self.assertEqual(sorted(os.listdir(TMP_DIR)), ['01.html', '01.log'])
        log_file_content = open(os.path.join(TMP_DIR, '01.log')).read()
        self.assertTrue('X-Engine' in log_file_content)


    def test_log_dir_request_content_is_empty(self):
        clear_directory(TMP_DIR)
        reset_request_counter()

        g = Grab(transport=GRAB_TRANSPORT)
        g.setup(log_dir=TMP_DIR)
        g.setup(headers={'X-Name': 'spider'}, post='xxxPost')

        self.assertEqual(os.listdir(TMP_DIR), [])
        g.go(SERVER.BASE_URL)
        self.assertEqual(sorted(os.listdir(TMP_DIR)), ['01.html', '01.log'])
        log_file_content = open(os.path.join(TMP_DIR, '01.log')).read()
        self.assertFalse('X-Name' in log_file_content)
        self.assertFalse('xxxPost' in log_file_content)

    def test_log_dir_request_content_headers_and_post(self):
        clear_directory(TMP_DIR)
        reset_request_counter()

        g = Grab(transport=GRAB_TRANSPORT)
        g.setup(log_dir=TMP_DIR, debug=True)
        g.setup(headers={'X-Name': 'spider'}, post={'xxx': 'Post'})

        self.assertEqual(os.listdir(TMP_DIR), [])
        g.go(SERVER.BASE_URL)
        self.assertEqual(sorted(os.listdir(TMP_DIR)), ['01.html', '01.log'])
        log_file_content = open(os.path.join(TMP_DIR, '01.log')).read()
        self.assertTrue('X-Name' in log_file_content)
        self.assertTrue('xxx=Post' in log_file_content)
