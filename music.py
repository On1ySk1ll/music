import sys
import sqlite3 as sql
from os import getcwd, scandir
from os.path import abspath, join
from tinytag import TinyTag
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QPixmap
from random import randint
from mutagen.id3 import ID3
from pathlib import Path
from pyautogui import size

# создание базы данных плейлистов  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
path = getcwd() + '\\music'
if Path(path).is_dir():
    pass
else:
    Path(path).mkdir()
if Path(path+'\\covers').is_dir():
    pass
else:
    Path(path+'\\covers').mkdir()
con = sql.connect(path + "\\playlist_music_data.db")
cur = con.cursor()
cur.execute("""
        CREATE TABLE IF NOT EXISTS music(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            full_name TEXT)""")
con.commit()
cur.execute("""
        CREATE TABLE IF NOT EXISTS playlists(
            id INTEGER PRIMARY KEY,
            name TEXT)""")
con.commit()
cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist_data(
            music_id INTEGER,
            playlist_id INTEGER)""")
con.commit()
cur.execute('SELECT name FROM playlists WHERE id=1;')
amc = cur.fetchone()
try: 
    amc[0]
except:
    cur.execute('INSERT INTO playlists(id, name) VALUES(?, ?)', (1, 'Вся Музыка'))
    con.commit()
# создание базы данных плейлистов  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# окно и система # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
app = QApplication(sys.argv)
app.setStyle('Fusion')

window = QWidget()
window.setWindowTitle('Музычка 2.1')

stack = QStackedLayout()
window.setLayout(stack)

grid_music = QGridLayout()
music_screen = QWidget()
music_screen.setLayout(grid_music)
stack.addWidget(music_screen)

audioout = QAudioOutput()
mediaplay = QMediaPlayer()
mediaplay.setAudioOutput(audioout)
# окно и система # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# поиск музыки из файлов # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
musicnames_all = []
with scandir(path) as entries:
    for entry in entries:
        if entry.name.endswith('.mp3'):
            tag = TinyTag.get(path + '/' + entry.name)
            if tag.artist and tag.title:
                musicnames_all.append((entry.name[0:-4], f'{tag.artist} ― {tag.title}'))
            else:
                musicnames_all.append((entry.name[0:-4], 'none'))
# поиск музыки из файлов # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# перенос музыки # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
cur.execute('SELECT file_name, full_name FROM music')
database_music = cur.fetchall()

for name in musicnames_all:
    if name not in database_music:
        cur.execute('INSERT INTO music(file_name, full_name) VALUES(?, ?)', (name[0], name[1]))
        con.commit()
        database_music.append(name)

for name in database_music:
    if name not in musicnames_all:
        cur.execute('DELETE FROM music WHERE file_name=?', (name[0],))
        con.commit()

cur.execute('SELECT id FROM music')
database_music_indexes = cur.fetchall()
cur.execute('SELECT music_id FROM playlist_data WHERE playlist_id=1')
database_playlist_data_indexes = cur.fetchall()

for id in database_music_indexes:
    if id not in database_playlist_data_indexes:
        cur.execute('INSERT INTO playlist_data(music_id, playlist_id) VALUES(?, ?)', (id[0], 1))
        con.commit()

all_indexes = []
for id in database_playlist_data_indexes:
    all_indexes.append(id[0])
# перенос музыки # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# файлы музыки # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
music_url = []
cur.execute('SELECT id, file_name, full_name FROM music')
musicnames_plus_id = cur.fetchall()
for name_id in musicnames_plus_id:
    if (name_id[1], name_id[2]) in musicnames_all:
        music_url.append((name_id[0], QUrl.fromLocalFile(path+'/'+name_id[1]+'.mp3')))
# файлы музыки # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# список музыки и выбор песни  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
list_music = QListWidget()

current_music_indexes = all_indexes
def choose_music():
    global paused, current_song
    music_name = list_music.currentItem().text()
    for name in musicnames_all:
            if name[1] == music_name:
                cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                break
            elif name[0] == music_name:
                cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                break
    index = cur.fetchone()[0]
    current_song = current_music_indexes.index(index)
    for id in music_url:
        if index == id[0]:
            mediaplay.setSource(id[1])
            for name in musicnames_plus_id:
                if name[0] == index:
                    yes_cover = False
                    for i in covers:
                        if i[0] == name[1]:
                            lbl_cover.setPixmap(i[1].scaled(250,250))
                            yes_cover = True
                            break
                    if not yes_cover:
                        lbl_cover.setPixmap(cover_def_pix.scaled(250,250))
                    break
    lbl_current.setText(music_name)
    if paused:
        btn_play.setText('▶')
        mediaplay.pause()
    else:
        btn_play.setText('■')
        mediaplay.play()
list_music.doubleClicked.connect(choose_music)
# список музыки и выбор песни  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Обложки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def extract_cover(path, img):
    try:
        audio = ID3(path)
        for tag in audio.values():
            if tag.FrameID == 'APIC':
                with open(img, 'wb') as img_file:
                    img_file.write(tag.data)
                return 1
    except:
        return 0
    return 0

covers = []
for name in musicnames_all:
    if extract_cover(path+'\\'+name[0]+'.mp3', path+'\covers\\'+name[0]+'.jpg'):
        covers.append((name[0], QPixmap(path+'\covers\\'+name[0]+'.jpg')))
    else:
        covers.append((0, 0))

try:
    cover_path = sys._MEIPASS
except Exception:
    cover_path = abspath('.')
cover_def_pix = QPixmap(join(cover_path, 'cover_default.png')).scaled(250,250)

lbl_cover = QLabel()
lbl_cover.setPixmap(cover_def_pix)
# Обложки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# список плейлистов и все штуки которые с ним связаны  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
current_playlist = 1
list_playlist = QListWidget()
line_name_playlist = QLineEdit()
line_name_playlist.setPlaceholderText('Имя плейлиста')

def update_playlists():
    list_playlist.clear()
    cur.execute('SELECT id, name FROM playlists')
    raw = cur.fetchall()
    for i in raw:
        list_playlist.addItem(str(i[0]) + ' : ' + i[1])

btn_create_playlist = QPushButton(text='Создать')
def add_playlist():
    name = line_name_playlist.text()
    if name:
        line_name_playlist.clear()
        cur.execute('SELECT id, name FROM playlists')
        raw = cur.fetchall()
        names = []
        playlist_ids = []
        for row in raw:
            names.append(row[1].lower())
            playlist_ids.append(row[0])
        if name.lower() not in names:
            for x in range(2, len(names)+2):
                if x not in playlist_ids:
                    cur.execute('INSERT INTO playlists(id, name) VALUES(?, ?)', (x, name))
                    con.commit()
            update_playlists()
        else:
            QMessageBox(text='Плейлист с таким именем уже существует').exec()
btn_create_playlist.clicked.connect(add_playlist)

btn_delete_playlist = QPushButton(text='Удалить')
def delete_playlist():
    name = line_name_playlist.text()
    if name.lower() == 'вся музыка':
        line_name_playlist.clear()
        QMessageBox(text="Нельзя 😋").exec()
    elif name:
        line_name_playlist.clear()
        cur.execute('SELECT name FROM playlists')
        names = cur.fetchall()
        if (name,) in names:
            cur.execute('SELECT id FROM playlists WHERE name=?', (name,))
            playlist_id = cur.fetchone()[0]
            cur.execute('DELETE FROM playlist_data WHERE playlist_id=?', (playlist_id,))
            con.commit()
            cur.execute('DELETE FROM playlists WHERE name=?', (name,))
            con.commit()
            update_playlists()
        else:
            QMessageBox(text='Не существует').exec()
btn_delete_playlist.clicked.connect(delete_playlist)

btn_add_music = QPushButton(text='Добавить музыку')
def add_music():
    index = list_playlist.currentItem().text().split(' : ')[0]
    music_name = list_music.currentItem().text()
    cur.execute('SELECT music_id FROM playlist_data WHERE playlist_id=?', (index,))
    ids = cur.fetchall()
    for name in musicnames_all:
            if name[1] == music_name:
                cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                break
            elif name[0] == music_name:
                cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                break
    music_index = cur.fetchone()[0]
    if (music_index,) not in ids:
        cur.execute('INSERT INTO playlist_data(music_id, playlist_id) VALUES(?, ?)', (music_index, index))
        con.commit()
btn_add_music.clicked.connect(add_music)

btn_remove_music = QPushButton(text='Убрать музыку')
def remove_music():
    playlist_index = int(list_playlist.currentItem().text().split(' : ')[0])
    if playlist_index != 1:
        music_name = list_music.currentItem().text()
        cur.execute('SELECT music_id FROM playlist_data WHERE playlist_id=?', (playlist_index,))
        ids = cur.fetchall()
        for name in musicnames_all:
            if name[1] == music_name:
                cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                break
            elif name[0] == music_name:
                cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                break
        music_index = cur.fetchone()[0]
        if (music_index,) in ids:
            cur.execute('DELETE FROM playlist_data WHERE music_id=? AND playlist_id=?', (music_index, playlist_index))
            con.commit()
            if playlist_index == current_playlist:
                global current_song, current_music_indexes
                current_song = 0
                list_music.clear()
                cur.execute('SELECT music_id FROM playlist_data WHERE playlist_id=?', (playlist_index,))
                raw = cur.fetchall()
                ids = []
                for i in raw:
                    ids.append(i[0])
                current_music_indexes = []
                for id in raw:
                    current_music_indexes.append(id[0])
                for name in musicnames_plus_id:
                    if name[0] in current_music_indexes:
                        if name[2] != 'none':
                            list_music.addItem(name[2])
                        else:
                            list_music.addItem(name[1])
                mediaplay.stop()
                global paused
                try:
                    music_name = list_music.item(0).text()
                    for name in musicnames_all:
                        if name[1] == music_name:
                            cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                            break
                        elif name[0] == music_name:
                            cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                            break
                    idk_index = cur.fetchone()[0]-1
                    for id in music_url:
                        if id[0] == idk_index:
                            mediaplay.setSource(id[1])
                            for name in musicnames_plus_id:
                                if name[0] == id[0]:
                                    if name[2] != 'none':
                                        lbl_current.setText(name[2])
                                    else:
                                        lbl_current.setText(name[1])
                    paused = True
                    btn_play.setText('▶')
                except AttributeError:
                    pass
btn_remove_music.clicked.connect(remove_music)

def choose_playlist():
    global current_playlist, current_music_indexes, current_song
    current_song = 0
    index = list_playlist.currentItem().text().split(' : ')[0]
    current_playlist = int(index)
    list_music.clear()
    cur.execute(f'SELECT music_id FROM playlist_data WHERE playlist_id={index}')
    raw = cur.fetchall()
    current_music_indexes = []
    for id in raw:
        current_music_indexes.append(id[0])
        for name in musicnames_plus_id:
            if id[0] == name[0]:
                if name[2] != 'none':
                    list_music.addItem(name[2])
                else:
                    list_music.addItem(name[1])
    mediaplay.stop()
    global paused
    try:
        music_name = list_music.item(0).text()
        for name in musicnames_all:
            if name[1] == music_name:
                cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                break
            elif name[0] == music_name:
                cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                break
        index = cur.fetchone()[0]-1
        for id in music_url:
            if id[0] == index:
                mediaplay.setSource(music_url[index][1])
                break
        for id in musicnames_plus_id:
            if id[0] == index+1:
                if id[2] != 'none':
                    lbl_current.setText(id[2])
                else:
                    lbl_current.setText(id[1])
                break
        paused = True
        btn_play.setText('▶')
    except AttributeError: pass
    for name in musicnames_plus_id:
        if name[0] == current_music_indexes[0]:
            yes_cover = False
            for i in covers:
                if i[0] == name[1]:
                    lbl_cover.setPixmap(i[1].scaled(250,250))
                    yes_cover = True
                    break
            if not yes_cover:
                lbl_cover.setPixmap(cover_def_pix.scaled(250,250))
list_playlist.doubleClicked.connect(choose_playlist)
# список плейлистов и все штуки которые с ним связаны  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# приготовления перед запуском # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if len(music_url) > 0:
    mediaplay.setSource(music_url[0][1])
    lbl_current = QLabel(text=musicnames_all[0][0])
    if covers[0][0] != 0:
        lbl_cover.setPixmap(covers[0][1].scaled(250,250))
    else:
        lbl_cover.setPixmap(cover_def_pix.scaled(250,250))
else:
    lbl_current = QLabel(text='Ничего')
paused = True
mode = 0
modes = {1 : False, 2 : True, 3 : True, 4 : False} # 0 - ничего, 1 - вверх, 2 - вниз, 3 - рандом, 4 - повтор
current_song = 0
# приготовления перед запуском # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# кнопка паузы # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
btn_play = QPushButton(text='▶')
def pause_button():
    global paused
    if paused:
        paused = False
        mediaplay.play()
        btn_play.setText('■')
    else:
        paused = True
        mediaplay.pause()
        btn_play.setText('▶')
btn_play.clicked.connect(pause_button)
# кнопка паузы # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# листать музыку # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def change_music(pos):
    if len(current_music_indexes) < 2:
        repeat_music()
    else:
        mediaplay.stop()
        music_name = list_music.item(pos).text()
        for name in musicnames_all:
            if name[1] == music_name:
                cur.execute('SELECT id FROM music WHERE full_name=?', (music_name,))
                break
            elif name[0] == music_name:
                cur.execute('SELECT id FROM music WHERE file_name=?', (music_name,))
                break
        index = cur.fetchone()[0]
        for id in music_url:
            if id[0] == index:
                list_music.setCurrentRow(current_music_indexes.index(id[0]))
                mediaplay.setSource(id[1])
                for name in musicnames_plus_id:
                    if name[0] == index:
                        yes_cover = False
                        for i in covers:
                            if i[0] == name[1]:
                                lbl_cover.setPixmap(i[1].scaled(250,250))
                                yes_cover = True
                                break
                        if not yes_cover:
                            lbl_cover.setPixmap(cover_def_pix.scaled(250,250))
                        break
                break
        lbl_current.setText(music_name)
        if paused:
            pass
        else:
            mediaplay.play()

btnsideleft = QPushButton(text='⇤')
def change_to_up():
    global current_song
    if current_song-1 < 0:
        current_song = len(current_music_indexes)-1
        change_music(current_song)
    else:
        current_song -= 1
        change_music(current_song)
btnsideleft.clicked.connect(change_to_up)

btnsideright = QPushButton(text='⇥')
def change_to_down():
    global current_song
    if current_song+1 > len(current_music_indexes)-1:
        current_song = 0
        change_music(current_song)
    else:
        current_song += 1
        change_music(current_song)
btnsideright.clicked.connect(change_to_down)
# листать музыку # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# громкость  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
slide_volume = QSlider(Qt.Orientation.Horizontal)
slide_volume.setMaximum(100)
slide_volume.setMinimum(0)
slide_volume.setPageStep(1)
slide_volume.setSliderPosition(100)
lbl_volume = QLabel(text='100%')
def volume_handler():
    audioout.setVolume(slide_volume.value()/100)
    lbl_volume.setText(str(slide_volume.value()) + '%')
slide_volume.valueChanged.connect(volume_handler)
# громкость  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# продолжительность  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
sltimex = 0
sltimey = 0
sltime_mouse_pressed = False
def slide_time_handle_mouse_move(event):
    global sltimex, sltimey
    sltimex = int(event.position().x())
    sltimey = int(event.position().y())
    if sltime_mouse_pressed:
        new = all_time - int((sltimex - 165)/-165 * all_time)
        slide_time.setValue(new)
        mediaplay.setPosition(slide_time.value())
        curtime = slide_time.value()
        text = lbl_time.text().split(' | ')
        if len(str((curtime//1000)%60)) < 2:
            lbl_time.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
        else:
            lbl_time.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])
def slide_time_handle_mouse_hold(event):
    global curtime, sltime_mouse_pressed
    mediaplay.pause()
    mediaplay.blockSignals(True)
    sltime_mouse_pressed = True
    new = all_time - int((sltimex - 165)/-165 * all_time)
    slide_time.setValue(new)
    mediaplay.setPosition(slide_time.value())
    curtime = slide_time.value()
    text = lbl_time.text().split(' | ')
    if len(str((curtime//1000)%60)) < 2:
        lbl_time.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
    else:
        lbl_time.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])
def slide_time_handle_mouse_release(event):
    global sltime_mouse_pressed
    sltime_mouse_pressed = False
    mediaplay.blockSignals(False)
    if not paused:
        mediaplay.play()
    current_position()

current_time = 0
all_time = 0
slide_time = QSlider(Qt.Orientation.Horizontal)
slide_time.setMaximum(1)
slide_time.setSliderPosition(0)
slide_time.setMouseTracking(True)
slide_time.mouseMoveEvent = slide_time_handle_mouse_move
slide_time.mousePressEvent = slide_time_handle_mouse_hold
slide_time.mouseReleaseEvent = slide_time_handle_mouse_release

lbl_time = QLabel(text='0:00 | 0:00')
def check_durarion():
    global all_time
    slide_time.setSliderPosition(0)
    all_time = mediaplay.duration()
    slide_time.setMaximum(all_time)
    if len(str((all_time//1000)%60)) < 2:
        lbl_time.setText(f'0:00 | {all_time//60000}:0{(all_time//1000)%60}')
    else:
        lbl_time.setText(f'0:00 | {all_time//60000}:{(all_time//1000)%60}')
mediaplay.durationChanged.connect(check_durarion)

def current_position():
    global current_time, paused
    current_time = mediaplay.position()
    slide_time.setSliderPosition(current_time)
    if current_time == all_time and mode:
        if mode > 2:
            if modes[mode]:
                random_music()
            else:
                repeat_music()
        else:
            if modes[mode]:
                change_to_up()
            else:
                change_to_down()
    elif current_time == all_time:
        paused = True
        mediaplay.pause()
        btn_play.setText('▶')
    text = lbl_time.text().split(' | ')
    if len(str((current_time//1000)%60)) < 2:
        lbl_time.setText(str(current_time//60000)+':0'+str((current_time//1000)%60)+' | '+text[1])
    else:
        lbl_time.setText(str(current_time//60000)+':'+str((current_time//1000)%60)+' | '+text[1])
mediaplay.positionChanged.connect(current_position)
# продолжительность  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# рандомная музыка # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def random_music():
    if len(current_music_indexes) < 2:
        repeat_music()
    else:
        mediaplay.stop()
        global current_song
        now = current_song
        current_song = randint(0, len(current_music_indexes)-1)
        while current_song == now:
            current_song = randint(0, len(current_music_indexes)-1)
        list_music.setCurrentRow(current_song)
        change_music(current_song)
# рандомная музыка # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# повтор # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def repeat_music():
    global paused, current_time
    paused = True
    mediaplay.pause()
    btn_play.setText('▶')
    current_time = 0
    mediaplay.setPosition(0)
    pause_button()
# повтор # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# авто воспроизведение # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
lbl_mode = QLabel(text='Ничего')

btn_auto_none = QPushButton(text='□')
def set_to_none():
    global mode
    mode = 0
    lbl_mode.setText('Ничего')
btn_auto_none.clicked.connect(set_to_none)

btn_auto_right = QPushButton(text='↪')
def set_to_right():
    global mode
    mode = 1
    lbl_mode.setText('Вниз')
btn_auto_right.clicked.connect(set_to_right)

btn_auto_left = QPushButton(text='↩')
def set_to_left():
    global mode
    mode = 2
    lbl_mode.setText('Вверх')
btn_auto_left.clicked.connect(set_to_left)

btn_auto_random = QPushButton(text='↭')
def set_to_random():
    global mode
    mode = 3
    lbl_mode.setText('Случайная')
btn_auto_random.clicked.connect(set_to_random)

btn_auto_repeat = QPushButton(text='↺')
def set_to_repeat():
    global mode
    mode = 4
    lbl_mode.setText('Повтор')
btn_auto_repeat.clicked.connect(set_to_repeat)
# авто воспроизведение # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# подсказки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
try:
    hint_path = sys._MEIPASS
except Exception:
    hint_path = abspath('.')
hint_window = QWidget()
hint_hbox = QHBoxLayout()
hint_window.setLayout(hint_hbox)
hint_window.setWindowTitle('Подсказочки')
pix = QPixmap(join(hint_path, 'hint.png'))
hint_lbl = QLabel()
hint_lbl.setPixmap(pix)
hint_hbox.addWidget(hint_lbl)

btn_hint = QPushButton(text='Помощь')
btn_hint.clicked.connect(lambda: hint_window.show())
# подсказки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# настройки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
grid_settings = QGridLayout()

settings_screen = QWidget()
settings_screen.setLayout(grid_settings)
stack.addWidget(settings_screen)

lbl_theme = QLabel('Светлая')
lbl_enable_cover = QLabel('Включено')

theme = 1
enable_cover = 1

if Path(path + '\\settings.txt').is_file():
    settings_file = open(path + '\\settings.txt', 'r')
    settings = settings_file.read().split('\n')
    settings.pop(0)
    parametres = {'theme' : 1, 'enable_cover' : 2}
   
    for s in settings:
        setting = s.split('=')
        thing = parametres[setting[0]]

        if thing == 1:
            if int(setting[1]):
                app.styleHints().setColorScheme(Qt.ColorScheme.Light)
            else:
                app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
                lbl_theme.setText('Тёмная')
                theme = 0

        elif thing == 2:
            if int(setting[1]):
                lbl_cover.show()
            else:
                lbl_cover.hide()
                lbl_enable_cover.setText('Выключено')
                enable_cover = 0

    settings_file.close()
else:
    settings_file = open(path + '\\settings.txt', 'w+')
    settings_file.write('''settings: theme - 0=dark, 1=light ; enable_cover - 0=disable, 1=enable
theme=1
enable_cover=1''')
    settings_file.close()

btn_settings = QPushButton(text='Настройки')
def to_settings():
    window.resize(int(screen_size_width * 0.364583), int(screen_size_height * 0.46296))
    music_screen.hide()
    settings_screen.show()
btn_settings.clicked.connect(to_settings)

btn_back_to_music = QPushButton(text='Назад')
def back_to_music():
    window.resize(int(screen_size_width * 0.46875), int(screen_size_height * 0.324))
    music_screen.show()
    settings_screen.hide()
btn_back_to_music.clicked.connect(back_to_music)

btn_theme = QPushButton(text='Сменить тему')
def change_theme():
    global theme, enable_cover
    if theme:
        theme = 0
        lbl_theme.setText('Тёмная')
        app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    else:
        theme = 1
        lbl_theme.setText('Светлая')
        app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    
    settings_file = open(path + '\\settings.txt', 'w+')
    settings_file.write(f'''settings: theme - 0=dark, 1=light ; enable_cover - 0=disable, 1=enable
theme={theme}
enable_cover={enable_cover}''')
    settings_file.close()
btn_theme.clicked.connect(change_theme)

btn_enable_cover = QPushButton(text='Вкл/Выкл Обложки')
def enable_disable_cover():
    global theme, enable_cover
    if enable_cover:
        enable_cover = 0
        lbl_enable_cover.setText('Выключено')
        lbl_cover.hide()
    else:
        enable_cover = 1
        lbl_enable_cover.setText('Включено')
        lbl_cover.show()

    settings_file = open(path + '\\settings.txt', 'w+')
    settings_file.write(f'''settings: theme - 0=dark, 1=light ; enable_cover - 0=disable, 1=enable
theme={theme}
enable_cover={enable_cover}''')
    settings_file.close()
btn_enable_cover.clicked.connect(enable_disable_cover)
# настройки  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# позиционирование # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
grid_music.addWidget(btn_settings, 0, 0)
grid_music.addWidget(list_music, 0, 5, 7, 1)
grid_music.addWidget(lbl_cover, 0, 0, 3, 3)

grid_music.addWidget(lbl_cover, 1, 0, 3, 3)

grid_music.addWidget(lbl_current, 4, 0, 1, 3)

grid_music.addWidget(slide_time, 5, 0, 1, 2)
grid_music.addWidget(lbl_time, 5, 2)

grid_music.addWidget(btn_play, 6, 1)
grid_music.addWidget(btnsideleft, 6, 0)
grid_music.addWidget(btnsideright, 6, 2)

grid_music.addWidget(lbl_mode, 7, 1)

grid_music.addWidget(btn_auto_left, 7, 0)
grid_music.addWidget(btn_auto_none, 8, 1)
grid_music.addWidget(btn_auto_right, 7, 2)

grid_music.addWidget(btn_auto_random, 8, 0)
grid_music.addWidget(btn_auto_repeat, 8, 2)

grid_music.addWidget(slide_volume, 9, 0, 1, 2)
grid_music.addWidget(lbl_volume, 9, 2)

grid_music.addWidget(list_music, 1, 5, 9, 1)

grid_music.addWidget(list_playlist, 1, 3, 6, 2)

grid_music.addWidget(line_name_playlist, 7, 3, 1, 2)

grid_music.addWidget(btn_create_playlist, 8, 3)
grid_music.addWidget(btn_delete_playlist, 8, 4)

grid_music.addWidget(btn_add_music, 9, 3)
grid_music.addWidget(btn_remove_music, 9, 4)

#
grid_settings.addWidget(btn_back_to_music, 0, 0)
grid_settings.addWidget(btn_theme, 0, 2)
grid_settings.addWidget(lbl_theme, 0, 3)

grid_settings.addWidget(btn_enable_cover, 1, 2)
grid_settings.addWidget(lbl_enable_cover, 1, 3)

grid_settings.addWidget(btn_hint, 2, 2)

# позиционирование # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

update_playlists()
list_playlist.setCurrentRow(0)
choose_playlist()
screen_size_width, screen_size_height = size()
window.resize(int(screen_size_width * 0.46875), int(screen_size_height * 0.324))
window.show()
app.exec()
