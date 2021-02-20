from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import rank

GOOD = 1
BAD = 0
CONTINUE = 2
OTHER = 3

class Tsumego(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://blacktoplay.com/?p=608')
        self.players = {}

    def fancy_click(self, id):
        self.driver.execute_script("arguments[0].click();", self.driver.find_element_by_id(id))

    def solution_check(self):
        solution_check = self.driver.find_element_by_id('solutionContainer')
        if solution_check.text == 'Completed!':
            self.fancy_click('loadButton')
            return GOOD
        elif solution_check.text == 'Wrong. Keep trying.':
            self.driver.execute_script("stepBeginning()")
            return BAD
        elif solution_check.text == 'Right, go on...':
            return CONTINUE
        else:
            return OTHER

    def place_stone(self, x, y, u):
        xc = x.lower()
        yc = chr(ord('a') - 1 + int(y))
        self.fancy_click(yc+xc)
        time.sleep(1)
        result = self.solution_check()

        if u not in self.players:
            self.players[u] = 0
        
        if result == GOOD:
            self.players[u]+= 1
            p = re.search(r'p=([0-9]+)', self.driver.current_url)
            message = f"HSWP {x}{y} was correct for problem {p.group(1)}! SeemsGood"
        elif result == BAD:
            self.players[u]-= 1
            message = f"{x}{y}? Try again! NotLikeThis"
        elif result == CONTINUE:
            message = f"{x}{y}? Keep going... O_o"
        else:
            message = f"{x}{y}?! WutFace"
        
        print(self.players)
        rank.update(self.players)
        
        return message

