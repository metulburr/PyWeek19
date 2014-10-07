

import pygame as pg
from .. import tools
from ..toolbox import button
import random
from data.tools import DB

import sys
import os

class Options(tools.States):
    def __init__(self, screen_rect, default, fullscreen):
        tools.States.__init__(self)
        self.fullscreen = fullscreen
        self.default_screensize = default
        self.screen_rect = screen_rect
        self.options = ['Back']
        self.next_list = ['MENU']
        self.pre_render_options()
        self.from_bottom = 300
        self.spacer = 35

        self.bg_orig = tools.Image.load('gavel.jpeg')
        self.bg = pg.transform.scale(self.bg_orig, (self.screen_rect.width, self.screen_rect.height))
        self.bg_rect = self.bg.get_rect(center=self.screen_rect.center)
        
        self.menu_item_bg_w = 200
        self.menu_item_bg_h = 25
        
        self.setup_buttons()
        
        self.notice, self.notice_rect = self.make_text(
            "Restart to apply settings correctly",
            (255,255,255),
            (self.screen_rect.centerx, self.screen_rect.top +25),
            24
        )
        
    def setup_buttons(self):
        self.buttons = []
        
        button_config = {
            "clicked_font_color" : (0,0,0),
            "hover_font_color"   : (205,195, 0),
            'font'               : tools.Font.load('impact.ttf', 18),
            'font_color'         : (255,255,255),
            'border_color'       : (0,0,0),
            'clicked_color'      : (255,255,255),
            'hover_color'        : (0,0,130),
        }
        width = 135
        height = 25
        if DB.load()['fullscreen']: #display opposite of current setting
            state = 'OFF'
        else:
            state = 'ON'
        self.fullscreen_toggle = button.Button((10,10,width,height),(0,0,100), 
            self.toggle_fullscreen, text='Fullscreen: {}'.format(state), **button_config)
        
        y = 40
        for res in DB.load()['resolution_options']:
            display = '{}x{}'.format(res[0], res[1])
            b = button.Button((10,y,width,height),(0,0,100), 
                lambda x=res:self.set_window(x), text=display, **button_config)
            self.buttons.append(b)
            y += 60
        '''
        self.window_button = button.Button((10,40,width,height),(0,0,100), 
            lambda:self.set_window((640,360)), text='640x360', **button_config)
        self.window2_button = button.Button((10,70,width,height),(0,0,100), 
            lambda:self.set_window((854,480)), text='854x480', **button_config)
        self.window3_button = button.Button((10,100,width,height),(0,0,100), 
            lambda:self.set_window((1280,720)), text='1280x720', **button_config)
        '''
        #self.default_button = button.Button((10,130,width,height),(0,0,100), 
        #    lambda:self.set_window(self.default_screensize), text=str(self.default_screensize[0])+'x'+str(self.default_screensize[1]), **button_config)
        self.sound_toggle = button.Button((10,160,width,height),(0,0,100), 
            self.toggle_sound, text='Sound', **button_config)
        self.music_toggle = button.Button((10,160,width,height),(0,0,100), 
            self.toggle_music, text='Music', **button_config)
        
        #self.buttons = [ self.window_button, #, self.default_button, self.fullscreen_toggle,
        #    self.window2_button, self.window3_button]#, self.sound_toggle, self.music_toggle]
        
        self.button_spacer = 30
        self.button_from_top = 80
        for i, btn in enumerate(self.buttons):
            btn.rect.center = (self.screen_rect.x + self.screen_rect.width//2, self.screen_rect.y + i * self.button_spacer + self.button_from_top)
    
    def toggle_fullscreen(self):
        self.change_res = 'fullscreen'
    def set_window(self, newsize):
        print('resolution change may require restart to take effect!!!')
        self.change_res = newsize
        db = DB.load()
        db['size'] = list(newsize)
        DB.save(db)
        
    def toggle_sound(self):
        self.change_sound = True
        #self.sound = not self.sound
    def toggle_music(self):
        self.music = not self.music

    def render_cursor(self, screen):
        mouseX, mouseY = pg.mouse.get_pos()
        self.cursor_rect = self.cursor.get_rect(center=(mouseX+10, mouseY+13))
        screen.blit(self.cursor, self.cursor_rect)

    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key in [pg.K_UP, pg.K_w]:
                self.change_selected_option(-1)
            elif event.key in [pg.K_DOWN, pg.K_s]:
                self.change_selected_option(1)
                
            elif event.key == pg.K_RETURN:
                self.select_option(self.selected_index)
        for button in self.buttons:
            button.check_event(event)
        self.switch_track_event(event)

        self.mouse_menu_click(event)

    def update(self, now, keys):
        self.mouse_hover_sound()
        self.change_selected_option()
        for i, btn in enumerate(self.buttons): #update button position in case of res change
            btn.rect.center = (self.screen_rect.x + self.screen_rect.width//2, self.screen_rect.y + i * self.button_spacer + self.button_from_top)
        self.bg = pg.transform.scale(self.bg_orig, (self.screen_rect.width, self.screen_rect.height))
        self.bg_rect = self.bg.get_rect(center=self.screen_rect.center)
        
    def render(self, screen):
        screen.fill((0,0,0))
        screen.blit(self.bg, self.bg_rect)
        screen.blit(self.notice, self.notice_rect)
        for i,opt in enumerate(self.rendered["des"]):
            aligned_center = (self.screen_rect.centerx, self.from_bottom+i*self.spacer)
            
            for option in self.options:
                w = self.menu_item_bg_w
                h = self.menu_item_bg_h
                #roundrects.round_rect(screen, (aligned_center[0]-(w//2), aligned_center[1]-(h//2),w,h), (0,0,0), 5, 2, (50,50,50))
            opt[1].center =  aligned_center
            if i == self.selected_index:
                rend_img,rend_rect = self.rendered["sel"][i]
                rend_rect.center = opt[1].center
                screen.blit(rend_img,rend_rect)
            else:
                rect = opt[1]
                screen.blit(opt[0],rect)
        for button in self.buttons:
            button.render(screen)
        
        
    def cleanup(self):
        pass
        
    def entry(self):
        self.bg = pg.transform.scale(self.bg_orig, (self.screen_rect.width, self.screen_rect.height))
        self.bg_rect = self.bg.get_rect(center=self.screen_rect.center)
