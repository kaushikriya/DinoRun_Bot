from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import os
import numpy as np
import cv2
import PIL


GAMMA = 0.99
OBSERVATION = 50000.
EXPLORE = 100000
FINAL_EPSILON = 0.0001
INITIAL_EPSILON = 0.1
REPLAY_MEMORY = 50000
BATCH = 32
FRAME_PER_ACTION = 1
ACTIONS=2
LEARNING_RATE=1e-4

class Game:
    def __init__(self, custom_config=True):
        chrome_options = Options()
        chrome_options.add_argument("disable-infobars")
        self._driver = webdriver.Chrome(executable_path='D:\chromedriver.exe', chrome_options=chrome_options)
        self._driver.set_window_position(x=-10, y=0)
        self._driver.set_window_size(200, 300)
        game_url='//chromedino.com/'
        self._driver.get(os.path.abspath(game_url))
        if custom_config:
            self._driver.execute_script("Runner.config.ACCELERATION=0")

    def get_crashed(self):
        return self._driver.execute_script("return Runner.instance_.crashed")

    def get_playing(self):
        return self._driver.execute_script("return Runner.instance_.playing")

    def restart(self):
        self._driver.execute_script("Runner.instance_.restart()")

        time.sleep(0.25)


    def press_up(self):
        self._driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)

    def get_score(self):
        score_array = self._driver.execute_script("return Runner.instance_.distanceMeter.digits")
        score = ''.join(
            score_array)
        return int(score)

    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")

    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")

    def end(self):
        self._driver.close()

class DinoAgent:
    def __init__(self,game):
        self._game = game
        self.jump()
        time.sleep(.5)
    def is_running(self):
        return self._game.get_playing()
    def is_crashed(self):
        return self._game.get_crashed()
    def jump(self):
        self._game.press_up()
    def duck(self):
        self._game.press_down()

class Game_sate:
    def __init__(self, agent, game):
        self._agent = agent
        self._game = game

    def get_state(self, actions):
        score = self._game.get_score()
        reward = 0.1 * score / 10
        is_over = False
        if actions[1] == 1:
            self._agent.jump()
            reward = 0.1 * score / 11
        image = grab_screen()

        if self._agent.is_crashed():
            self._game.restart()
            reward = -11 / score
            is_over = True
        return image, reward, is_over


def grab_screen(_driver=None):
    screen = np.array(PIL.ImageGrab.grab(bbox=(40, 180, 440, 400)))
    image = process_img(screen)
    return image


def process_img(image):

    image = cv2.resize(image,(20,40))
    image = image[2:38, 10:50]
    image = cv2.Canny(image, threshold1=100, threshold2=200)
    return image