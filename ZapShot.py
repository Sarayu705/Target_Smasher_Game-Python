import math
import random
import time
import pygame
pygame.init()

width,height=800,600
win=pygame.display.set_mode((width,height))
pygame.display.set_caption("ZapShot")

target_increment=600
target_event=pygame.USEREVENT
target_padding=40
bg_color=(18,18,18)
top_bar_height=50
labelFont=pygame.font.SysFont("comicsans", 24)

lives=5
game_duration=60

pop_sound=pygame.mixer.Sound("pop.wav")

class Target:
    
    def __init__(self,x,y,color="red",secondColor="white",maxSize=40,growthRate=0.2):
        self.x = x
        self.y = y
        self.color = color
        self.secondColor = secondColor
        self.maxSize = maxSize
        self.growthRate = growthRate
        self.size = 0
        self.grow = True
        self.is_blue = False
        
    def update(self):
        if(self.size+self.growthRate>=self.maxSize):
            self.grow=False
        if self.grow:
            self.size+=self.growthRate
        else:
            self.size-=self.growthRate
        
    def draw(self,win):
        pygame.draw.circle(win, self.color, (self.x, self.y), int(self.size))
        pygame.draw.circle(win, self.secondColor,(self.x, self.y), int(self.size * 0.8))
        pygame.draw.circle(win, self.color, (self.x, self.y), int(self.size * 0.6))
        pygame.draw.circle(win, self.secondColor,(self.x, self.y), int(self.size * 0.4))
        
    def collide(self, x, y):
        dis = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dis<=self.size

def draw(win, targets,combo_text,combo_display_time):
    win.fill(bg_color)

    for target in targets:
        target.draw(win)
        
    if combo_text and time.time()-combo_display_time<1.0:
        combo_label=labelFont.render(combo_text,1,"yellow")
        win.blit(combo_label,(get_middle(combo_label),80))
        
def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(win, remaining_time, score, hits,clicks):
    pygame.draw.rect(win, "grey", (0, 0, width, top_bar_height))
    time_label = labelFont.render(f"Time: {format_time(remaining_time)}", 1, "black")
    score_label = labelFont.render(f"Score: {score}", 1, "black")
    hits_label = labelFont.render(f"Hits: {hits}", 1, "black")
    acc = round(hits / clicks * 100, 1) if clicks > 0 else 0
    acc_label = labelFont.render(f"Acc: {acc}%", 1, "black")

    win.blit(time_label, (5, 5))
    win.blit(score_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(acc_label, (650, 5))


def end_screen(win, elapsed_time, hits, clicks,score):
    win.fill(bg_color)
    time_label = labelFont.render(f"Time: {format_time(elapsed_time)}", 1, "white")
    score_label = labelFont.render(f"Score: {score}", 1, "white")
    hits_label = labelFont.render(f"Hits: {hits}", 1, "white")
    acc = round(hits / clicks * 100, 1) if clicks > 0 else 0
    acc_label = labelFont.render(f"Accuracy: {acc}%", 1, "white")

    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(score_label, (get_middle(score_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(acc_label, (get_middle(acc_label), 400))

    pygame.display.update()
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                #exit()


def get_middle(surface):
    return width / 2 - surface.get_width()/2


def main():
    run=True
    targets=[]
    clock=pygame.time.Clock()
    
    zapshots=0
    clicks=0
    score = 0
    current_combo = 0
    combo_text = ""
    combo_display_time = 0
    start_time=time.time()
    
    pygame.time.set_timer(target_event, target_increment)
    
    while(run):
        clock.tick(60)
        click=False
        mouse_pos=pygame.mouse.get_pos()
        elapsed_time=time.time()-start_time
        remaining_time = max(0, game_duration - elapsed_time)
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                break
            
            if event.type == target_event:
                x = random.randint(target_padding, width-target_padding)
                y = random.randint(target_padding+top_bar_height, height-target_padding)
                if random.random() < 0.2:  
                    target = Target(x, y, color="blue", secondColor="white", maxSize=25, growthRate=0.4)
                    target.is_blue = True
                else:
                    target = Target(x, y)
                    target.is_blue = False
                targets.append(target)
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                click=True
                clicks+=1
                
        for target in targets[:]:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                current_combo = 0
                combo_text = ""

            elif click and target.collide(*mouse_pos):
                pop_sound.play()
                targets.remove(target)
                zapshots += 1
                current_combo += 1

                if target.is_blue:
                    score += 10
                else:
                    score += 1

                if current_combo == 5:
                    score += 5
                    combo_text = "Combo x3!"
                    combo_display_time = time.time()
                elif current_combo == 10:
                    score += 10
                    combo_text = "Combo x10!"
                    combo_display_time = time.time()

        if remaining_time <= 0:
            end_screen(win, elapsed_time, zapshots, clicks, score)
            
        draw(win, targets, combo_text, combo_display_time)
        draw_top_bar(win, remaining_time, score, zapshots, clicks)
        pygame.display.update()

    pygame.quit()
    
main()