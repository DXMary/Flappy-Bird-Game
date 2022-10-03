from tkinter.tix import MAIN
import pygame, sys
import time
import os
import random
from buttons import Button
import webbrowser

# WIN SETUP 

WIN_WIDTH = 480
WIN_HEIGHT = 730
PIPE_VEL = 3
FLOOR = 640

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

# FONT SETUP

pygame.font.init() 

TITLE_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird Game/assets/AquireBold-8Ma60.otf", 50)
MAIN_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird Game/assets/AquireBold-8Ma60.otf", 25)
SCORE_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird Game/assets/Aquire-BW0ox.otf", 90)

DRAW_LINES = False

# INITIATE CONSTANTS, IMAGES AND MUSIC

base_img = pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Base.png"))
bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Bluebird-upflap.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Bluebird-midflap.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Bluebird-downflap.png")))]
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Pipe.png")))
bg_img = pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird Game/assets/Background.jpeg"))
bg_music = [pygame.mixer.init(),pygame.mixer.music.load("/Users/user/Desktop/Flappy Bird Game/assets/Background-music.mp3"),
        pygame.mixer.music.set_volume(0.1),
        pygame.mixer.music.play(-1)] #change
score_sound = pygame.mixer.Sound("/Users/user/Desktop/Flappy Bird Game/assets/score.wav")
flap_sound = pygame.mixer.Sound("/Users/user/Desktop/Flappy Bird Game/assets/wing.wav")
fall_sound = pygame.mixer.Sound("/Users/user/Desktop/Flappy Bird Game/assets/die.wav")
hit_sound = pygame.mixer.Sound("/Users/user/Desktop/Flappy Bird Game/assets/hit.wav")
white = (255, 255, 255)
black = (0, 0, 0)
red =  (255, 0, 0)

# BIRD SETUP

class Bird:
    
    WIN_HEIGHT = 0
    WIN_WIDTH = 0
    MAX_ROTATION = 25
    IMGS = bird_imgs
    ROT_VEL = 20
    ANIMATION_TIME =  7

    def __init__(self, x, y): 
        self.x = x
        self.y = y
        self.gravity = 9.8
        self.tilt = 0 
        self.tick_count = 0 
        self.vel = 0 
        self.height = self.y 
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):

        self.tick_count += 1

        displacement = self.vel*self.tick_count + 0.5*(3)*self.tick_count**2

        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):

        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]  
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]  
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]  
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]  
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# PIPE SETUP

class Pipe:

    GAP = 200
    VEL= 5
    WIN_HEIGHT = WIN_HEIGHT
    WIN_WIDTH = WIN_WIDTH

    def __init__(self, x):

        self.x = x
        self.heigh = 0
        self.gap = 20

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False
        self.set_height()

    def set_height(self):

        self.height = random.randrange(50,480)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):

        self.x -= self.VEL

    def draw(self, win):

        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

# BASE SETUP

class Base:

    VEL = 5
    WIN_WIDTH = WIN_WIDTH
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):

        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG,(self.x1, self.y))
        win.blit(self.IMG,(self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

# END SCREEN

def end_screen(win): 

    pygame.display.set_caption("GAME OVER")
    
    while True:

        win.fill("black")

        MENU_TEXT = TITLE_FONT.render("GAME OVER", True, white)
        MENU_RECT = MENU_TEXT.get_rect(center=(240, 140))

        MENU_MOUSE_POS = pygame.mouse.get_pos()
        RESTART_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect2.jpeg"), pos=(240, 270), 
                            text_input="RESTART", font=MAIN_FONT, base_color="White", hovering_color="Gray")
        QUIT_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect2.jpeg"), pos=(240, 380), 
                            text_input="QUIT", font=MAIN_FONT, base_color="White", hovering_color="Gray")
        MENU_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect2.jpeg"), pos=(240, 490), 
                            text_input="MAIN MENU", font=MAIN_FONT, base_color="White", hovering_color="Gray")

        WIN.blit(MENU_TEXT, MENU_RECT)
        
        for button in [RESTART_BUTTON, QUIT_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.music.rewind()
                    Game(win)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
                if MENU_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main_menu(win)
                

        pygame.display.update()


# DRAW WINDOW

def draw_window(win, bird, pipes, base, score):

    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)
    
    base.draw(win)
    
    bird.draw(win)
    
    # SCORE

    score_label = SCORE_FONT.render("" + str(score), True, white)
    win.blit(score_label, (210, 40))

    pygame.display.update()

# GAME LOOP
    
def Game (win):

    pygame.display.set_caption("CYBERPUNK FLAPPY BIRD")

    bird = Bird(230, 350)
    pipes = [Pipe(600)]
    base = Base(FLOOR)
    score = 0
    clock = pygame.time.Clock()
    start = False
    lost = False
    run = True

    while run:

        clock.tick(30)
           
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN and not lost:
                if event.key == pygame.K_SPACE:
                    if not start:
                        start = True
                    bird.jump()
                    flap_sound.play()
                    
        if start:
            bird.move()
        if not lost:
            base.move()

            if start:
                rem = []
                add_pipe = False
                for pipe in pipes:
                    pipe.move()
                    
                    if pipe.collide(bird, win):
                        lost = True
                        hit_sound.play()

                    if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                        rem.append(pipe)

                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        add_pipe = True

                if add_pipe:
                    score += 1
                    pipes.append(Pipe(600))

                for r in rem:
                    pipes.remove(r)


        if bird.y + bird_imgs[0].get_height() - 10 >= FLOOR:
            fall_sound.play()
            break

        draw_window(WIN, bird, pipes, base, score)
    
    end_screen(WIN)

# MAIN MENU

def main_menu(win):

    pygame.display.set_caption("CYBERPUNK FLAPPY BIRD | MAIN MENU")

    run = True

    while run:

        WIN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = TITLE_FONT.render("MAIN MENU", True, white)
        MENU_RECT = MENU_TEXT.get_rect(center=(240, 140))

        PLAY_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect.jpeg"), pos=(240, 270), 
                            text_input="PLAY", font=MAIN_FONT, base_color="White", hovering_color="Gray")
        QUIT_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect.jpeg"), pos=(240, 380), 
                            text_input="QUIT", font=MAIN_FONT, base_color="White", hovering_color="Gray")
        CREDITS_BUTTON = Button(image=pygame.image.load("/Users/user/Desktop/Flappy Bird Game/assets/Rect.jpeg"), pos=(240, 490), 
                            text_input="CREDITS", font=MAIN_FONT, base_color="White", hovering_color="Gray")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON, CREDITS_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Game(win)
                if CREDITS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    webbrowser.open('https://github.com/DXMary/Flappy-Bird-Game', new=2) 
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu(WIN)
