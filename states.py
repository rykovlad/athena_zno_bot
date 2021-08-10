import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem


class TestStates(Helper):
    mode = HelperMode.snake_case

    SUBJECT_SELECTION_MENU = ListItem()
    MAIN_TESTING1 = ListItem()
    # TEST_STATE_1 = ListItem()
    # TEST_STATE_2 = ListItem()
    # TEST_STATE_3 = ListItem()
    # TEST_STATE_4 = ListItem()
    # TEST_STATE_5 = ListItem()
