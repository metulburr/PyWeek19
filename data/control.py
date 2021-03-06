
import os
import pygame as pg
from .states import menu, splash, game, options
from .states.new_session import part1, part2, part3, part4
from data.tools import DB

class Control():
    def __init__(self, **settings):
        self.__dict__.update(settings)
        pg.mixer.pre_init(44100, -16, 1, 512)
        pg.init()
        self.monitor = (pg.display.Info().current_w, pg.display.Info().current_h)
        self.add_monitor_res()
        pg.display.set_caption(self.caption)
        self.default_screensize = (int(self.size[0]), int(self.size[1]))
        self.screensize = (int(self.size[0]), int(self.size[1]))
        if self.fullscreen:
            self.screen = pg.display.set_mode(self.screensize, pg.FULLSCREEN)
        else:
            if self.resizable:
                self.screen = pg.display.set_mode(self.screensize, pg.RESIZABLE)
            else:
                os.environ["SDL_VIDEO_CENTERED"] = "True"
                self.screen = pg.display.set_mode(self.screensize)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.keys = pg.key.get_pressed()
        self.done = False
        self.state_dict = {
            "MENU"     : menu.Menu(self.screen_rect),
            "SPLASH"   : splash.Splash(self.screen_rect),
            #'TITLE'    : title.Title(self.screen_rect),
            'GAME'     : game.Game(self.screen_rect),
            'OPTIONS'  : options.Options(self.screen_rect, self.default_screensize, self.fullscreen),
            
            'PART1'   : part1.Part1(self.screen_rect),
            'PART2'   : part2.Part2(self.screen_rect),
            'PART3'   : part3.Part3(self.screen_rect),
            'PART4'   : part4.Part4(self.screen_rect),
        }

        self.state_name = "SPLASH"
        self.state = self.state_dict[self.state_name]
        
    def add_monitor_res(self):
        db = DB.load()
        if list(self.monitor) not in db['resolution_options']:
            db['resolution_options'].append(self.monitor)
            DB.save(db)
            
    def check_display_change(self):
        if self.state.change_res:
            pg.display.quit()
            pg.display.init()
            pg.display.set_caption(self.caption)
            if self.state.change_res == 'fullscreen':
                if not self.fullscreen:
                    self.screen = pg.display.set_mode(self.screensize, pg.FULLSCREEN)
                else:
                    os.environ["SDL_VIDEO_CENTERED"] = "True"
                    self.screen = pg.display.set_mode(self.screensize)
                    self.size == self.screensize
                self.fullscreen = not self.fullscreen
                self.screen_rect = self.screen.get_rect()
                
            else:
                self.fullscreen = False
                self.screen = pg.display.set_mode(self.state.change_res)
                self.screen_rect = self.screen.get_rect()
            self.save_settings()
            self.state.change_res = None
            self.screen_rect = self.screen.get_rect()
            if self.state_name == 'OPTIONS':
                self.state.setup_buttons() #options state only method (update buttons status for ON and OFF)
            
    def save_settings(self):
        db = DB.load()
        db['fullscreen'] = self.fullscreen
        db['difficulty'] = self.difficulty
        db['size']       = self.state.change_res
        db['caption']    = self.caption
        db['resizable']  = self.resizable
        DB.save(db)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
            elif event.type in (pg.KEYDOWN,pg.KEYUP):
                self.keys = pg.key.get_pressed()
                

            elif event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode(event.size, pg.RESIZABLE)
                self.screen_rect = self.screen.get_rect()
            self.state.get_event(event, self.keys)

    def change_state(self):
        if self.state.done:
            self.state.cleanup()
            self.state_name = self.state.next
            self.state.done = False
            self.state = self.state_dict[self.state_name]
            self.state.screen_rect = self.screen.get_rect() #update if changed screen resolution
            self.state.entry()


    def run(self):
        while not self.done:
            if self.state.quit:
                self.done = True
            self.check_display_change()
            self.state.screen_rect = self.screen.get_rect() #update if changed screen resolution
            now = pg.time.get_ticks()
            self.event_loop()
            self.change_state()
            self.state.update(now, self.keys)
            self.state.render(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)


