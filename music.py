import sys
import sqlite3 as sql
from os import getcwd, scandir
from tinytag import TinyTag
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from random import randint

# feat Nikita aka On1ySk1ll

# создание базы данных плейлистов #
path = getcwd() + '\music'
con = sql.connect(path + "\playlist_music_data.db")
cur = con.cursor()
cur.execute("""
        CREATE TABLE IF NOT EXISTS music(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT)""")
con.commit()
cur.execute("""
        CREATE TABLE IF NOT EXISTS playlists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    cur.execute('INSERT INTO playlists(name) VALUES(?)', ('All',))
    con.commit()

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = QWidget()
window.setWindowTitle('музычка 1.5')

audioout = QAudioOutput()
mediaplay = QMediaPlayer()
mediaplay.setAudioOutput(audioout)

# загрузка музыки #
musicnamestemp = []
with scandir(path) as entries:
    for entry in entries:
        if entry.name.endswith('.mp3'):
            tag = TinyTag.get(path + '/' + entry.name)
            if tag.artist and tag.title:
                musicnamestemp.append((entry.name, f'{tag.artist} ― {tag.title}'))
            else:
                musicnamestemp.append((entry.name, 'none'))
music = []
for i in range(len(musicnamestemp)):
    music.append((i+1, QUrl.fromLocalFile(path + '/' + musicnamestemp[i][0])))

# список музыки #
musicnames = []
musiclist = QListWidget()
for i in range(len(musicnamestemp)):
    if musicnamestemp[i][1] == "none":
        musiclist.addItem(musicnamestemp[i][0][:-4])
        musicnames.append((i+1, musicnamestemp[i][0][:-4]))
    else:
        musiclist.addItem(musicnamestemp[i][1])
        musicnames.append((i+1, musicnamestemp[i][1]))
musiclist.setCurrentRow(0)
names = []
for i in musicnames:
    names.append(i[1])
def choosemusic():
    global paused
    music_name = musiclist.item(musiclist.currentRow()).text()
    cur.execute('SELECT id FROM music WHERE name=?', (music_name,))
    index = cur.fetchone()[0]
    for i in music:
        if i[0] == index:
            mediaplay.setSource(i[1])
            lblcur.setText(names[i[0]-1])
            paused = False
            btnstart.setText('■')
            mediaplay.play()
            break
musiclist.doubleClicked.connect(choosemusic)

# перенос музыки #
cur.execute('SELECT name FROM music')
raw = cur.fetchall()
dbmusic = []
for i in raw:
    dbmusic.append(i[0])
for name in names:
    if name not in dbmusic:
        cur.execute('INSERT INTO music(name) VALUES(?)', (name,))
        con.commit()
        dbmusic.append(name[1])
for name in dbmusic:
    if name not in names:
        cur.execute(f'DELETE FROM music WHERE name={name}')
        con.commit()
cur.execute('SELECT id FROM music')
cur_indexs = cur.fetchall()
cur.execute('SELECT music_id FROM playlist_data WHERE playlist_id=1')
db_indexs = cur.fetchall()
indexs = []
for i in db_indexs:
    indexs.append(i)
curmusicids = []
for i in cur_indexs:
    curmusicids.append(i[0])
    if i not in indexs:
        cur.execute('INSERT INTO playlist_data(music_id, playlist_id) VALUES(?,?)', (i[0], 1))
        con.commit()

# список плейлистов и все штуки которые с ним связаны #
curplaylist = 1
listplaylist = QListWidget()
btnaddplaylist = QPushButton(text='Create')
btndeleteplaylist = QPushButton(text='Delete')
linenameplaylist = QLineEdit()
linenameplaylist.setPlaceholderText('Playlist Name')
btnaddmusic = QPushButton(text='Add Music')
btnremovemusic = QPushButton(text='Remove Music')

def update_playlists():
    listplaylist.clear()
    cur.execute('SELECT id, name FROM playlists')
    raw = cur.fetchall()
    for i in raw:
        listplaylist.addItem(str(i[0]) + ' : ' + i[1])
update_playlists()

def add_playlist():
    name = linenameplaylist.text()
    if name:
        linenameplaylist.clear()
        cur.execute('SELECT name FROM playlists')
        raw = cur.fetchall()
        names = []
        for i in raw:
            names.append(i[0].lower())
        if name.lower() not in names:
            cur.execute('INSERT INTO playlists(name) VALUES(?)', (name,))
            con.commit()
            update_playlists()
        else:
            QMessageBox(text='Already Exists').exec()
btnaddplaylist.clicked.connect(add_playlist)

def delete_playlist():
    name = linenameplaylist.text()
    if name.lower() == 'all':
        linenameplaylist.clear()
    elif name:
        linenameplaylist.clear()
        cur.execute('SELECT name FROM playlists')
        raw = cur.fetchall()
        names = []
        for i in raw:
            names.append(i[0].lower())
        if name.lower() in names:
            cur.execute(f'DELETE FROM playlists WHERE name=?', (name,))
            con.commit()
            update_playlists()
        else:
            QMessageBox(text='Not Exists').exec()
btndeleteplaylist.clicked.connect(delete_playlist)

def add_music():
    name = linenameplaylist.text()
    if name.lower() != 'all' and name:
        cur.execute('SELECT id FROM playlists WHERE name=?', (name,))
        index = cur.fetchone()[0]
        cur_music_name = musiclist.item(musiclist.currentRow()).text()
        cur.execute(f'SELECT music_id FROM playlist_data WHERE playlist_id={index}')
        raw = cur.fetchall()
        ids = []
        for i in raw:
            ids.append(i[0])
        cur.execute('SELECT id FROM music WHERE name=?', (cur_music_name,))
        music_index = cur.fetchone()[0]
        if music_index not in ids:
            cur.execute('INSERT INTO playlist_data(music_id, playlist_id) VALUES(?, ?)', (music_index, index))
            con.commit()
btnaddmusic.clicked.connect(add_music)

def remove_music():
    name = linenameplaylist.text()
    all_names = []
    cur.execute('SELECT name FROM playlists')
    raw = cur.fetchall()
    for i in raw:
        all_names.append(i[0])
    if name.lower() != 'all' and name in all_names:
        cur.execute('SELECT id FROM playlists WHERE name=?', (name,))
        index = cur.fetchone()[0]
        cur_music_name = musiclist.item(musiclist.currentRow()).text()
        cur.execute(f'SELECT music_id FROM playlist_data WHERE playlist_id={index}')
        raw = cur.fetchall()
        ids = []
        for i in raw:
            ids.append(i[0])
        cur.execute('SELECT id FROM music WHERE name=?', (cur_music_name,))
        music_index = cur.fetchone()[0]
        if music_index in ids:
            cur.execute('DELETE FROM playlist_data WHERE music_id=? AND playlist_id=?', (music_index, index))
            con.commit()
            if index == curplaylist:
                global curmusicids, pos
                pos = 0
                musiclist.clear()
                cur.execute(f'SELECT music_id FROM playlist_data WHERE playlist_id={index}')
                raw = cur.fetchall()
                ids = []
                for i in raw:
                    ids.append(i[0])
                curmusicids = ids
                for i in music:
                    if i[0] in ids:
                        musiclist.addItem(names[i[0]-1])
                mediaplay.stop()
                global paused
                music_name = musiclist.item(0).text()
                cur.execute('SELECT id FROM music WHERE name=?', (music_name,))
                index = cur.fetchone()[0]
                for i in music:
                    if i[0] == index:
                        mediaplay.setSource(i[1])
                        lblcur.setText(names[i[0]-1])
                        paused = True
                        btnstart.setText('▶')
                        break
    else:
        QMessageBox(text='Not Exists').exec()
btnremovemusic.clicked.connect(remove_music)

def choose_playlist():
    global curplaylist, curmusicids, pos
    pos = 0
    index = listplaylist.currentItem().text().split(' : ')[0]
    curplaylist = int(index)
    musiclist.clear()
    cur.execute(f'SELECT music_id FROM playlist_data WHERE playlist_id={index}')
    raw = cur.fetchall()
    ids = []
    for i in raw:
        ids.append(i[0])
    curmusicids = ids
    for i in music:
        if i[0] in ids:
            musiclist.addItem(names[i[0]-1])
    mediaplay.stop()
    global paused
    music_name = musiclist.item(0).text()
    cur.execute('SELECT id FROM music WHERE name=?', (music_name,))
    index = cur.fetchone()[0]
    for i in music:
        if i[0] == index:
            mediaplay.setSource(i[1])
            lblcur.setText(names[i[0]-1])
            paused = True
            btnstart.setText('▶')
            break
listplaylist.doubleClicked.connect(choose_playlist)
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #

mediaplay.setSource(music[0][1])
paused = True
lblcur = QLabel(text=names[0])
mode = 0
modes = {1 : False, 2 : True, 3 : True, 4 : False}
pos = 0

# кнопка паузы #
def start():
    global paused
    if paused:
        paused = False
        mediaplay.play()
        btnstart.setText('■')
    else:
        paused = True
        mediaplay.pause()
        btnstart.setText('▶')

# листать музыку #
def change_music(pos):
    mediaplay.stop()
    music_name = musiclist.item(pos).text()
    cur.execute('SELECT id FROM music WHERE name=?', (music_name,))
    index = cur.fetchone()[0]
    for i in music:
        if i[0] == index:
            mediaplay.setSource(i[1])
            lblcur.setText(names[i[0]-1])
            if paused:
                pass
            else:
                mediaplay.play()
            break

def change_to_up():
    global pos
    if pos-1 < 0:
        pos = len(curmusicids)-1
        change_music(pos)
    else:
        pos -= 1
        change_music(pos)
        
def change_to_down():
    global pos
    if pos+1 > len(curmusicids)-1:
        pos = 0
        change_music(pos)
    else:
        pos += 1
        change_music(pos)

# громкость #
def volumeslide():
    audioout.setVolume(slidevol.value()/100)
    lblvol.setText(str(slidevol.value()) + '%')

# продолжительность #
def check_dur():
    global alltime
    slidetime.setSliderPosition(0)
    alltime = mediaplay.duration()
    slidetime.setMaximum(alltime)
    if len(str((alltime//1000)%60)) < 2:
        lbltime.setText(f'0:00 | {alltime//60000}:0{(alltime//1000)%60}')
    else:
        lbltime.setText(f'0:00 | {alltime//60000}:{(alltime//1000)%60}')

# рандомная музыка # ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ ПЕРЕДЕЛАТЬ
def random_music():
    mediaplay.stop()
    global pos
    now = pos
    pos = randint(0, len(curmusicids)-1)
    if len(curmusicids) == 1:
        change_music(pos)
    else:
        while pos == now:
            pos = randint(0, len(curmusicids)-1)
        change_music(pos)

# продолжительность + автовоспроизведение #
def cur_pos():
    global curtime, paused
    curtime = mediaplay.position()
    slidetime.setSliderPosition(curtime)
    if curtime == alltime and mode:
        if mode > 2:
            if modes[mode]:
                random_music()
            else:
                paused = True
                mediaplay.pause()
                btnstart.setText('▶')
                curtime = 0
                mediaplay.setPosition(0)
                start()
        else:
            if modes[mode]:
                change_to_up()
            else:
                change_to_down()
            start() 
    elif curtime == alltime:
        paused = True
        mediaplay.pause()
        btnstart.setText('▶')
    text = lbltime.text().split(' | ')
    if len(str((curtime//1000)%60)) < 2:
        lbltime.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
    else:
        lbltime.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])

# слайдер продолжительности #
sltimex = 0
sltimey = 0
sltime_mouse_pressed = False
def slide_time_handle_mouse_move(event):
    global sltimex, sltimey
    sltimex = int(event.position().x())
    sltimey = int(event.position().y())
    if sltime_mouse_pressed:
        new = alltime - int((sltimex - 165)/-165 * alltime)
        slidetime.setValue(new)
        mediaplay.setPosition(slidetime.value())
        curtime = slidetime.value()
        text = lbltime.text().split(' | ')
        if len(str((curtime//1000)%60)) < 2:
            lbltime.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
        else:
            lbltime.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])
def slide_time_handle_mouse_click(event):
    global curtime, sltime_mouse_pressed
    mediaplay.pause()
    mediaplay.blockSignals(True)
    sltime_mouse_pressed = True
    new = alltime - int((sltimex - 165)/-165 * alltime)
    slidetime.setValue(new)
    mediaplay.setPosition(slidetime.value())
    curtime = slidetime.value()
    text = lbltime.text().split(' | ')
    if len(str((curtime//1000)%60)) < 2:
        lbltime.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
    else:
        lbltime.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])
def slide_time_handle_mouse_unclick(event):
    global sltime_mouse_pressed
    sltime_mouse_pressed = False
    mediaplay.blockSignals(False)
    if not paused:
        mediaplay.play()
    cur_pos()

# авто воспроизведение #
def settonone():
    global mode
    mode = 0
    lblmode.setText('none')
def settoleft():
    global mode
    mode = 1
    lblmode.setText('next-up')
def settoright():
    global mode
    mode = 2
    lblmode.setText('next-down')
def settorandom():
    global mode
    mode = 3
    lblmode.setText('next-random')
def settorepeat():
    global mode
    mode = 4
    lblmode.setText('repeat')

grid = QGridLayout()

# кнопка паузы #
btnstart = QPushButton(text='▶')
btnstart.clicked.connect(start)

# листать музыку #
btnsideright = QPushButton(text='⇥')
btnsideright.clicked.connect(change_to_down)
btnsideleft = QPushButton(text='⇤')
btnsideleft.clicked.connect(change_to_up)

# громкость #
slidevol = QSlider(Qt.Orientation.Horizontal)
slidevol.setMaximum(100)
slidevol.setMinimum(0)
slidevol.setPageStep(1)
slidevol.setSliderPosition(100)
slidevol.valueChanged.connect(volumeslide)
lblvol = QLabel(text='100%')

mediaplay.durationChanged.connect(check_dur)
mediaplay.positionChanged.connect(cur_pos)

# продолжительность #
curtime = 0
alltime = 0
slidetime = QSlider(Qt.Orientation.Horizontal)
slidetime.setMaximum(1)
slidetime.setSliderPosition(0)
slidetime.setMouseTracking(True)
slidetime.mouseMoveEvent = slide_time_handle_mouse_move
slidetime.mousePressEvent = slide_time_handle_mouse_click
slidetime.mouseReleaseEvent = slide_time_handle_mouse_unclick
lbltime = QLabel(text='0:00 | 0:00')

# кнопка автовоспроизведения #
btnautonone = QPushButton(text='□')
btnautonone.clicked.connect(settonone)
btnautoleft = QPushButton(text='↩')
btnautoleft.clicked.connect(settoleft)
btnautoright = QPushButton(text='↪')
btnautoright.clicked.connect(settoright)
btnautorandom = QPushButton(text='↭')
btnautorandom.clicked.connect(settorandom)
btnautorepeat = QPushButton(text='↺')
btnautorepeat.clicked.connect(settorepeat)
lblmode = QLabel(text='none')

grid.addWidget(lblcur, 0, 0, 1, 3)

grid.addWidget(slidetime, 1, 0, 1, 2)
grid.addWidget(lbltime, 1, 2)

grid.addWidget(btnstart, 2, 0, 1, 3)

grid.addWidget(btnsideleft, 3, 0)
grid.addWidget(lblmode, 3, 1)
grid.addWidget(btnsideright, 3, 2)

grid.addWidget(btnautoleft, 4, 0)
grid.addWidget(btnautonone, 4, 1)
grid.addWidget(btnautoright, 4, 2)

grid.addWidget(btnautorandom, 5, 0)
grid.addWidget(btnautorepeat, 5, 2)

grid.addWidget(slidevol, 6, 0, 1, 2)
grid.addWidget(lblvol, 6, 2)

grid.addWidget(musiclist, 0, 5, 7, 1)

grid.addWidget(listplaylist, 0, 3, 4, 2)

grid.addWidget(linenameplaylist, 4, 3, 1, 2)

grid.addWidget(btnaddplaylist, 5, 3)
grid.addWidget(btndeleteplaylist, 5, 4)

grid.addWidget(btnaddmusic, 6, 3)
grid.addWidget(btnremovemusic, 6, 4)

window.setLayout(grid)
window.show()
app.exec()