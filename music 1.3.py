import sys
from os import getcwd, scandir
from tinytag import TinyTag
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from random import randint

# feat Nikita

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = QWidget()
window.setWindowTitle('музычка')

audioout = QAudioOutput()
mediaplay = QMediaPlayer()
mediaplay.setAudioOutput(audioout)

# загрузка музыки #
path = getcwd() + '\music'
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
for name in musicnamestemp:
    music.append(QUrl.fromLocalFile(path + '/' + name[0]))

# список музыки #
musicnames = []
musiclist = QListWidget()
for name in musicnamestemp:
    if name[1] == "none":
        musiclist.addItem(name[0][:-4])
        musicnames.append(name[0][:-4])
    else:
        musiclist.addItem(name[1])
        musicnames.append(name[1])
musiclist.setCurrentRow(0)
def choosemusic():
    global pos, paused
    pos = musiclist.currentRow()
    mediaplay.setSource(music[pos])
    lblcur.setText(musicnames[pos])
    paused = False
    btnstart.setText('■')
    mediaplay.play()
musiclist.doubleClicked.connect(choosemusic)

mediaplay.setSource(music[0])
paused = True
length = len(music) - 1
pos = 0
lblcur = QLabel(text=musicnames[0])
mode = 0
modes = {1 : False, 2 : True, 3 : True, 4 : False}

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
def changemusic(side):
    mediaplay.stop()
    btnstart.setText('▶')
    global pos, paused
    paused = True
    if side:
        if pos + 1 > length:
            pos = 0
            mediaplay.setSource(music[pos])
            lblcur.setText(musicnames[pos])
            musiclist.setCurrentRow(pos)
        else:
            pos += 1
            mediaplay.setSource(music[pos])
            lblcur.setText(musicnames[pos])
            musiclist.setCurrentRow(pos)
    else:
        if pos - 1 < 0:
            pos = length 
            mediaplay.setSource(music[pos])
            lblcur.setText(musicnames[pos])
            musiclist.setCurrentRow(pos)
        else:
            pos -= 1
            mediaplay.setSource(music[pos])
            lblcur.setText(musicnames[pos])
            musiclist.setCurrentRow(pos)

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

# рандомная музыка #
def random_music():
    mediaplay.stop()
    global pos
    now = pos
    pos = randint(0, len(musicnames)-1)
    while pos == now:
        pos = randint(0, len(musicnames)-1)
    mediaplay.setSource(music[pos])
    lblcur.setText(musicnames[pos])
    musiclist.setCurrentRow(pos)
    mediaplay.play()

# продолжительность + автовоспроизведение #
def cur_pos():
    global curtime, paused
    curtime = mediaplay.position()
    slidetime.setSliderPosition(curtime)
    if curtime == alltime and mode:
        slidetime.releaseMouse()
        slidetime.setValue(0)
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
            changemusic(modes[mode])
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
def slide_time_moving():
    global curtime
    mediaplay.setPosition(slidetime.value())
    curtime = slidetime.value()
    text = lbltime.text().split(' | ')
    if len(str((curtime//1000)%60)) < 2:
        lbltime.setText(str(curtime//60000)+':0'+str((curtime//1000)%60)+' | '+text[1])
    else:
        lbltime.setText(str(curtime//60000)+':'+str((curtime//1000)%60)+' | '+text[1])
def slide_time_press():
    mediaplay.blockSignals(True)
    mediaplay.pause()
def slide_time_release():
    mediaplay.blockSignals(False)
    if not paused:
        mediaplay.play()

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
btnsideright.clicked.connect(lambda: changemusic(True))
btnsideleft = QPushButton(text='⇤')
btnsideleft.clicked.connect(lambda: changemusic(False))

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
slidetime.sliderMoved.connect(slide_time_moving)
slidetime.sliderPressed.connect(slide_time_press)
slidetime.sliderReleased.connect(slide_time_release)
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

grid.addWidget(musiclist, 0, 3, 7, 1)

window.setLayout(grid)
window.show()
app.exec()
