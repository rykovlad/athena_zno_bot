from aiogram.utils.helper import Helper, HelperMode, ListItem


class TestStates(Helper):
    mode = HelperMode.snake_case

    SUBJECT_SELECTION_MENU = ListItem()
    MAIN_TESTING1 = ListItem()
