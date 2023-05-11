import os
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
Builder.load_file('./musicplayer.kv')


class MusicPlayer(BoxLayout):
    playlist = ObjectProperty(None)
    current_song_label = ObjectProperty(None)
    song_position_label = ObjectProperty(None)
    song_duration_label = ObjectProperty(None)
    sound = None
    song_duration = NumericProperty(0)
    song_position = NumericProperty(0)
    is_playing = BooleanProperty(False)
    playlist_image = StringProperty('/home/pi/Desktop/app_icons/Menu.png')
    play_pause_image = StringProperty('/home/pi/Desktop/app_icons/play_icon.png')
    next_icon_image = StringProperty('/home/pi/Desktop/app_icons/next_icon.png')
    previous_icon_image = StringProperty('/home/pi/Desktop/app_icons/previous_icon.png')
    last_player_state = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(MusicPlayer, self).__init__(**kwargs)
        self.load_songs()
        if self.playlist:
            self.play_song(self.playlist)
            self.stop_song()

    def load_songs(self):
        music_folder = '/home/pi/Music'
        for song in os.listdir(music_folder):
            if song.endswith('.mp3'):
                btn = Button(text=song, size_hint_y=None, height=40)
                btn.bind(on_release=self.play_song)
                self.ids.playlist_box.add_widget(btn)
        if len(self.ids.playlist_box.children) > 0:
            self.playlist = self.ids.playlist_box.children[0]
            self.play_song(self.ids.playlist_box.children[0])

    def play_song(self, btn):
        music_folder = '/home/pi/Music'
        song_path = os.path.join(music_folder, btn.text)
        if self.sound is not None:
            self.sound.stop()
            self.song_position = 0
        self.sound = SoundLoader.load(song_path)
        if self.sound:
            self.song_duration = self.sound.length
            self.current_song_label.text = btn.text
            if self.last_player_state:
                self.is_playing = False
                self.stop_song()
            else:
                self.is_playing = True
                self.sound.play()
                Clock.schedule_interval(self.update_song_position, 1 / 60)
                self.update_song_duration_label()
                self.update_play_pause_button()

    def update_song_position(self, dt):
        if self.sound is not None:
            self.song_position = self.sound.get_pos()
            self.update_song_position_label()

    def update_song_duration_label(self):
        minutes = int(self.song_duration // 60)
        seconds = int(self.song_duration % 60)
        self.song_duration_label.text = f"{minutes:02d}:{seconds:02d}"

    def update_song_position_label(self):
        minutes = int(self.song_position // 60)
        seconds = int(self.song_position % 60)
        self.song_position_label.text = f"{minutes:02d}:{seconds:02d}"
    def stop_song(self):
        if self.sound is not None:
            if self.is_playing:
                self.sound.stop()
                self.is_playing = False
                self.last_player_state = True
            else:
                self.sound.play()
                self.is_playing = True
                self.last_player_state = False
        self.update_play_pause_button()

    def next_song(self):
        if self.playlist is not None:
            index = self.ids.playlist_box.children.index(self.playlist)
            if index < len(self.ids.playlist_box.children) - 1:
                next_btn = self.ids.playlist_box.children[index + 1]
                self.play_song(next_btn)

    def previous_song(self):
        if self.playlist is not None:
            index = self.ids.playlist_box.children.index(self.playlist)
            if index > 0:
                previous_btn = self.ids.playlist_box.children[index - 1]
                self.play_song(previous_btn)

    def on_touch_up(self, touch):
        if self.sound is not None and self.ids.song_progress.collide_point(*touch.pos):
            progress = (touch.pos[0] - self.ids.song_progress.x) / self.ids.song_progress.width
            self.sound.seek(progress * self.sound.length)

    def update_play_pause_button(self):
        if self.is_playing:
            self.play_pause_image = '/home/pi/Desktop/app_icons/pause_icon.png'
        else:
            self.play_pause_image = '/home/pi/Desktop/app_icons/play_icon.png'
            
    def open_second_screen(self):
        second_screen = BoxLayout(orientation='vertical')
        playlist_box = GridLayout(cols=1, size_hint=(1, 0.8))
        for song in self.ids.playlist_box.children:
            btn = Button(text=song.text, size_hint_y=None, height=40)
            btn.bind(on_release=self.play_song)
            playlist_box.add_widget(btn)
        second_screen.add_widget(playlist_box)
        close_button = Button(text='Close', size_hint=(1, 0.1))
        close_button.bind(on_release=self.close_second_screen)
        second_screen.add_widget(close_button)
        self.popup_window = Popup(title='Songs', content=second_screen, size_hint=(0.8, 0.8))
        self.popup_window.open()

    def close_second_screen(self, instance):
        self.popup_window.dismiss()
        
class MusicApp(App):
    def build(self):
        return MusicPlayer()

if __name__ == '__main__':
    MusicApp().run()
