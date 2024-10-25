import pygame
import sys
import time
from pygame import mixer
from ultralytics import YOLO
from picamera2 import Picamera2
from libcamera import ColorSpace
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.display.init()
SCREEN = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Fruits Identifier")

# Initialize GPIO
GPIO.setmode(GPIO.BC)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Load the YOLO model
model = YOLO('fruits.t')
cof_level = 0.7

# Directories for language files
english_directory = "English/"
tagalog_directory = "Tagalog/"

# Mapping class IDs to file names within the Speech directory
english_sound_mapping = {i: english_directory + f"{i}.WAV" for (10)}
tagalog_sound_mapping = {i: tagalog_directory + f"{i}.WAV" for i in range(10)}

# Sound effect initialization
mixer.init()
click_sound = pygame.mixer.Sound("src/marimba3.wav")
capture_sound = pygame.mixer.Sound("src/click.wav")

# Button class for GUI buttons
class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color = base_color
        self.hoveg_color = hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.hovered = True
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.hovered = False
            self.text = self.font.render(self.text_input, True, self.base_color)

    def playClickSound(self, position):
        if self.rect.collidepoint(position):
            click_sound.play()

def play_music():
    initial_volume = 0.5
    pygame.mixer.music.set_volume(initial_volume)
    pygame.mixer.music.load("src/mainBGSounds.wav")

def get_font(size):
    return pygame.font.Font("src/LydoraKids.ttf", size)

# Main menu screen
def main_menu():
    display_info = pygame.display.Info()
    SCREEN = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
    BG = pygame.image.load("src/mainGUI.jpg")
    initial_volume = 0.5
    play_music()

    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BUTTON = Button(image=pygame.image.load("src/playButton.png"), pos=(320, 228),
                             text_input="", font=get_font(60), base_color=(228, 84, 39),
                             hovering_color=(255, 255, 255))
        HOWTOPLAY_BUTTON = Button(image=pygame.image.load("src/howtoPlay.png"),
                                  text_input="", font=get_font(60), base_color=(228, 84, 39),
                                  hovering_color=(255, 255, 255))
        ABOUT_BUTTON = Button(image=pygame.image.load("src/about.png"), pos=(320, 430),
                              text_input="", font=get_font(60), base_color=(228, 84, 39),
                              hovering_color=(255, 255, 255))
        for button in [PLAY_BUTTON, HOWTOPLAY_BUTTON, ABOUT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.get_mods() & pygame.KMOD_ALT:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    PLAY_BUTTON.playClickSound(MENU_MOUSE_POS)
                    start_game(SCREEN)
                if HOWTOPLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    HOWTOPLAY_BUTTON.playClickSound(MENU_MOUSE_POS)
                    play_howtoplay(SCREEN)
                if ABOUT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    ABOUT_BUTTON.playClickSound(MENU_MOUSE_POS)
                    play_about(SCREEN)
        pygame.display.update()

# Function to start the game
def start_game(SCREEN):
    running = True
    initial_volume = 0.5
    pygame.mixer.music.set_volume(initial_volume)

    while running:
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        BG = pygame.image.load("src/selectLanguage.jpg")
        SCREEN.blit(BG, (0, 0))
        ENGLISH_BUTTON = Button(image=pygame.image.load("src/Options Rect.jpg"), pos=(180, 300),
                                text_input="ENGLISH", font=get_font(60), base_color=(228, 84, 39),
                                hovering_color=(255, 255, 255))
        TAGALOG_BUTTON = Button(image=pygame.image.load("src/Options Rect.jpg"), pos=(470, 300),
                                text_input="TAGALOG", font=get_font(60), base_color=(228, 84, 39),
                                hovering_color=(255, 255, 255))
        BACK_BUTTON = Button(image=pygame.image.load("src/backButton.png"), pos=(85, 70),
                             text_input="", font=get_font(50), base_color=(255, 255, 255),
                             hovering_color=(0, 255, 0))
        for button in [ENGLISH_BUTTON, TAGALOG_BUTTON, BACK_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in [ENGLISH_BUTTON, TAGALOG_BUTTON, BACK_BUTTON]:
                    button.changeColor(MENU_MOUSE_POS)
                if ENGLISH_BUTTON.checkForInput(MENU_MOUSE_POS):
                    ENGLISH_BUTTON.playClickSound(MENU_MOUSE_POS)
                    play_english(SCREEN)
                if TAGALOG_BUTTON.checkForInput(MENU_MOUSE_POS):
                    TAGALOG_BUTTON.playClickSound(MENU_MOUSE_POS)
                    play_tagalog(SCREEN)
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    BACK_BUTTON.playClickSound(MENU_MOUSE_POS)
                    return
        pygame.display.update()

# Function to play in English language
def play_english(SCREEN):
    print("Transitioning to the English screen...")
    running = True
    camera_running = True
    pygame.mixer.music.set_volume(0.3)
    while running:
        try:
            appWidth = 640
            appHeight = 480
            camera = Picamera2()
            configPreview = camera.create_preview_configuration()
            camera.preview_configuration.main.size = (appWidth, appHeight)
            camera.preview_configuration.main.format = 'BGR888'
            camera.configure('preview')
            configStill = camera.create_still_configuration()
            camera.still_configuration.enable_raw()
            camera.still_configuration.main.size = camera.sensor_resolution
            camera.still_configuration.buffer_count = 2
            camera.still_configuration.colour_space = ColorSpace.Sycc()
            camera.start()
            display_info = pygame.display.Info()
            while running:
                PLAY_MOUSE_POS = pygame.mouse.get_pos()
                SCREEN.fill((0, 0, 0))
                array = camera.capture_array()
                previewFrame = pygame.image.frombuffer(array.data, (appWidth, appHeight), 'RGB')
                SCREEN.blit(previewFrame, (0, 0))
                PLAY_BACK = Button(image=pygame.image.load("src/backButton.png"), pos=(85, 70),
                                   text_input="", font=get_font(50), base_color=(255, 255, 255),
                                   hovering_color=(0, 255, 0))
                PLAY_BACK.changeColor(PLAY_MOUSE_POS)
                PLAY_BACK.update(SCREEN)
                if GPIO.input(21) == GPIO.LOW:
                    filename = 'captured_image.jpg'
                    camera.capture_file(filename)
                    capture_sound.play()
                    results = model(filename, conf=conf_level)
                    for result in results:
                         if result:
                             box = result.boxes[0]
                             class_id = int(box.cls.item())
                             sound_file = english_sound_mapping.get(class_id)
                             if sound_file:
                                 fruit_sound = pygame.mixer.Sound(sound_file)
                                 pygame.mixer.music.set_volume(0.1)
                                 fruit_sound.play()
                         else:
                            fruit_sound = pygame.mixer.Sound('en_nodetection.WAV')
                            pygame.mixer.music.set_volume(0.1)
                            fruit_sound.play()
                    time.sleep(7)
                    pygame.mixer.music.set_volume(0.3)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
                            running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        PLAY_BACK.playClickSound(PLAY_MOUSE_POS)
                        if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                            running = False
                            break
                pygame.display.update()
            camera.stop()
            camera.close()
        except Exception as e:
            print("Error:", e)
            camera_running = False
        if not camera_running:
            return

# Function to play in Tagalog language
def play_tagalog(SCREEN):
    print("Transitioning to the Tagalog screen...")
    running = True
    camera_running = True
    pygame.mixer.music.set_volume(0.3)
    while running:
        try:
            appWidth = 640
            appHeight = 480
            camera = Picamera2()
            configPreview = camera.create_preview_configuration()
            camera.preview_configuration.main.size = (appWidth, appHeight)
            camera.preview_configuration.main.format = 'BGR888'
            camera.configure('preview')
            configStill = camera.create_still_configuration()
            camera.still_configuration.enable_raw()
            camera.still_configuration.main.size = camera.sensor_resolution
            camera.still_configuration.buffer_count = 2
            camera.still_configuration.colour_space = ColorSpace.Sycc()
            camera.start()
            display_info = pygame.display.Info()
            while running:
                PLAY_MOUSE_POS = pygame.mouse.get_pos()
                SCREEN.fill((0, 0, 0))
                array = camera.capture_array()
                previewFrame = pygame.image.frombuffer(array.data, (appWidth, appHeight), 'RGB')
                SCREEN.blit(previewFrame, (0, 0))
                PLAY_BACK = Button(image=pygame.image.load("src/backButton.png"), pos=(85, 70),
                                   text_input="", font=get_font(50), base_color=(255, 255, 255),
                                   hovering_color=(0, 255, 0))
                PLAY_BACK.changeColor(PLAY_MOUSE_POS)
                PLAY_BACK.update(SCREEN)
                if GPIO.input(21) == GPIO.LOW:
                    filename = 'captured_image.jpg'
                    camera.capture_file(filename)
                    capture_sound.play()
                    results = model(filename, conf=conf_level)
                    for result in results:
                         if result:
                             box = result.boxes[0]
                             class_id = int(box.cls.item())
                             sound_file = tagalog_sound_mapping.get(class_id)
                             if sound_file:
                                 fruit_sound = pygame.mixer.Sound(sound_file)
                                 pygame.mixer.music.set_volume(0.1)
                                 fruit_sound.play()
                         else:
                            fruit_sound = pygame.mixer.Sound('tl_nodetection.WAV')
                            pygame.mixer.music.set_volume(0.1)
                            fruit_sound.play()
                    time.sleep(7)
                    pygame.mixer.music.set_volume(0.3)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
                            running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        PLAY_BACK.playClickSound(PLAY_MOUSE_POS)
                        if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                            running = False
                            break
                pygame.display.update()
            camera.stop()
            camera.close()
        except Exception as e:
            print("Error:", e)
            camera_running = False
        if not camera_running:
            return

# Function to play the how to play screen
def play_howtoplay(SCREEN):
    print("Transitioning to the How To Play screen...")
    running = True
    while running:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        BG = pygame.image.load("src/howtoPlay.jpg")
        SCREEN.blit(BG, (0, 0))
        PLAY_BACK = Button(image=pygame.image.load("src/backButton.png"), pos=(90, 70),
                           text_input="", font=get_font(50), base_color=(255, 255, 255),
                           hovering_color=(0, 255, 0))
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                PLAY_BACK.playClickSound(PLAY_MOUSE_POS)
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    running = False
                    break
        pygame.display.update()

# Function to play the about screen
def play_about(SCREEN):
    print("Transitioning to the About screen...")
    running = True
    while running:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        BG = pygame.image.load("src/aboutUs.jpg")
        SCREEN.blit(BG, (0, 0))
        PLAY_BACK = Button(image=pygame.image.load("src/backButton.png"), pos=(90, 70),
                           text_input="", font=get_font(50), base_color=(255, 255, 255),
                           hovering_color=(0, 255, 0))
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                PLAY_BACK.playClickSound(PLAY_MOUSE_POS)
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    running = False
                    break
        pygame.display.update()

# Start the main menu
main_menu()
