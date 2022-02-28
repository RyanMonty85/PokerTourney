#App for Poker Tournaments
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
import sounddevice as sd
import soundfile as sf

#gui config
class BoxLayoutExample(BoxLayout):
    #setting init variables
    playercount = 0
    rebuycount = 0
    buyincount = 0
    levelcount = 5
    payoutcount = 1
    poolcount = 0
    count = 0
    nextlevel = 0
    prevlevel = 0
    timer_sec = 0
    timer_start = False
    min_display = 20
    sec_display = 0
    break_set = 0
    break_test = 0
    start_aud = "horn"
    warn_aud = "warn"
    
    #init stringproperties
    main_text = StringProperty("0")
    rebuy_text = StringProperty("0")
    buyin_text = StringProperty("$0")
    level_text = StringProperty("5:00")
    payout_text = StringProperty("1")
    pool_text = StringProperty("$0")
    payoutamount_text = StringProperty("NA")
    firstamount_text = StringProperty("First: $0")
    secondamount_text = StringProperty("Second: $0")
    thirdamount_text = StringProperty("Third: $0")
    fourthamount_text = StringProperty("Fourth: $0")
    fifthamount_text = StringProperty("Fifth: $0")
    start_text = StringProperty("5:00")
    blinds_text = StringProperty("5/10")
    timer_text = StringProperty("5:00")
    minutes_text = StringProperty("5")
    seconds_text = StringProperty("00")

    #calculating payouts and prize pool via user input
    def payout_calc(self):
        paysched = [1, .7, .5, .5, .4, 0, .3, .3, .25, .25, 0, 0, .2, .15, .2, 0, 0, 0, .1, .1, 0, 0, 0, 0, .05]
        self.poolcount = self.buyincount * (self.rebuycount+self.playercount)
        self.pool_text = str(f"${self.poolcount}") 
        self.winpool = [self.poolcount * paysched[self.payoutcount-1], self.poolcount * paysched[self.payoutcount+4], self.poolcount * paysched[self.payoutcount+9], self.poolcount * paysched[self.payoutcount+14], self.poolcount * paysched[self.payoutcount+19]]
       
        self.firstamount_text = str(f"First: ${self.winpool[0]}")   
      
        self.secondamount_text = str(f"Second: ${self.winpool[1]}")

        self.thirdamount_text = str(f"Third: ${self.winpool[2]}")   

        self.fourthamount_text = str(f"Fourth: ${self.winpool[3]}")

        self.fifthamount_text = str(f"Fifth: ${self.winpool[4]}")
    #add player function
    def player_button_click(self):
        self.playercount += 1
        self.main_text = str(self.playercount)
        self.payout_calc()
    def rem_player_button_click(self):
        if self.playercount > 0:
            self.playercount -= 1
            self.main_text = str(self.playercount)
            self.payout_calc()
    #add rebuy function
    def rebuy_button_click(self):
        self.rebuycount += 1
        self.rebuy_text = str(self.rebuycount)
        self.payout_calc()
    def rem_rebuy_button_click(self):
        if self.rebuycount > 0:
            self.rebuycount -= 1
            self.rebuy_text = str(self.rebuycount)
            self.payout_calc()
    #increase buying function
    def buyin_button_click(self):
        self.buyincount += 5
        self.buyin_text = str(f"${self.buyincount}")
        self.payout_calc() 
    def lower_buyin_button_click(self):
        if self.buyincount > 0:
            self.buyincount -= 5
            self.buyin_text = str(f"${self.buyincount}")
            self.payout_calc() 
    #increase level function
    def level_button_click(self):
        self.levelcount += 5
        self.level_text = str(f"{self.levelcount}:00")
        self.start_text = str(f"{self.levelcount}:00")
        self.timer_text = str(f"{self.levelcount}:00")
    def lower_level_button_click(self):
        if self.levelcount > 5:
            self.levelcount -= 5
            self.level_text = str(f"{self.levelcount}:00")
            self.start_text = str(f"{self.levelcount}:00")
            self.timer_text = str(f"{self.levelcount}:00")
    #increase payout places function
    def payout_button_click(self):
        if self.payoutcount < 5:
            self.payoutcount += 1
            self.payout_text = str(self.payoutcount)
            self.payout_calc() 
    def lower_payout_button_click(self):
        if self.payoutcount > 1:
            self.payoutcount -= 1
            self.payout_text = str(self.payoutcount)
            self.payout_calc() 
    #next level function 
    def next_level_click(self):
        if self.nextlevel < 19 and self.break_set < 1:
            self.nextlevel += 1
        self.small = [5, 10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 2500]
        self.big = [10, 25, 50, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 3000, 4000, 5000]
        self.blinds_text = str(f"{self.small[self.nextlevel]}/{self.big[self.nextlevel]}")
    #previous level display function
    def prev_level_click(self):
        if self.nextlevel > 0:
            self.nextlevel -= 1
            self.blinds_text = str(f"{self.small[self.nextlevel]}/{self.big[self.nextlevel]}")
    #break function
    def break_level(self):
        self.break_set = 1 
    def break_level_reset(self):
        self.break_set = 0
        self.break_test = 0
    #level countdown timer/sound function
    def update_time(self, nap):
            if self.break_test != 1:
                self.start_aud = "horn"
                self.warn_aud = "warn"
            if self.break_test == 1:
                self.start_aud = "break"
                self.warn_aud = "breakwarn"
            if self.timer_start:
                self.timer_sec += nap
            minutes, seconds = divmod(self.timer_sec, 60)
            self.sec_display = 60 - seconds
            self.min_display = (self.levelcount - 1) - minutes
            if int(self.min_display) == 0 and int(self.sec_display) < 1:
                self.timer_sec = 0
                if self.break_test == 0:
                    self.break_test = self.break_set
                else:
                    self.break_level_reset()
                self.next_level_click()
            self.timer_text = f'{int(self.min_display):02d}:{int(self.sec_display):02d}'
            if int(self.sec_display) == 59 and int(self.min_display) == int(self.levelcount -1):
                filename = f'{self.start_aud}.wav'
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
            if int(self.sec_display) == 55 and int(self.min_display) == int(self.levelcount - 1) and self.break_set == 0:
                filename = f'l{self.nextlevel + 1}.wav'
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
            if int(self.sec_display) == 00 and int(self.min_display) == 1:
                filename = f'{self.warn_aud}.wav'
                data, fs = sf.read(filename, dtype='float32')
                sd.play(data, fs)
    #boolean function for level timer
    def on_start(self):
        if self.timer_start:
            Clock.schedule_interval(self.update_time, 0)
        else: Clock.unschedule(self.update_time)
    #start level function
    def start_stop(self):
        self.timer_start = not self.timer_start
        self.on_start()
    #reset level function
    def reset_clock(self):
        self.min_display = 0
        self.timer_sec = 0


class PokerDonksApp(App):
    pass


PokerDonksApp().run()