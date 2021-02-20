from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

class Tsumego(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://blacktoplay.com/?p=608')
        self.users = {}

    def fancy_click(self, id):
        self.driver.execute_script("arguments[0].click();", self.driver.find_element_by_id(id))

    def solution_check(self):
        solution_check = self.driver.find_element_by_id('solutionContainer')
        if solution_check.text == 'Completed!':
            self.fancy_click('loadButton')
            return 'Correct'
        elif solution_check.text == 'Wrong. Keep trying.':
            self.driver.execute_script("stepBeginning()")
            return 'Wrong'
        return 'Keep trying'

    def place_stone(self, coords, u):
        self.fancy_click(coords)
        time.sleep(1)
        result = self.solution_check()
        if u not in self.users:
            self.users[u] = 0
        if result == 'Correct':
            self.users[u]+= 1
        elif result == 'Wrong':
            self.users[u]-= 1
        
        print(self.users)
        
        return result

