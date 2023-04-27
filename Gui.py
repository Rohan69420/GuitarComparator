import PySimpleGUI as sg
import pyaudio
import numpy as np

"""Audio to Frequency plot """

# VARS CONSTS:
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([])}

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('Black')
FrameWidth = 900
FrameHeight = 500

#GUI layout
layout = [[sg.Graph(canvas_size=(FrameWidth, FrameHeight),
                    graph_bottom_left=(-16, -16),
                    graph_top_right=(116, 116),
                    background_color='#B9B9B9',
                    key='graph')],
          [sg.ProgressBar(4000, orientation='h',
                          size=(20, 20), key='-PROG-')],
          [sg.Button('Listen', font=AppFont),
           sg.Button('Stop', font=AppFont, disabled=True),
           sg.Button('Exit', font=AppFont)]]
_VARS['window'] = sg.Window('Mic to basic fft plot + Max Level',
                            layout, finalize=True)

graph = _VARS['window']['graph']

# INIT vars:
CHUNK = 128  # Samples: 1024,  512, 256, 128 <<<<<ALSO THE SIZE OF NP ARRAY
RATE = 4800  # Going double the peak frequency range of standard 5 stringed acoustic guitar: 1200Hz
INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 10  # In ms for the event loop
GAIN = 10
pAud = pyaudio.PyAudio()

# FUNCTIONS:


def drawAxis():
    graph.DrawLine((0, 50), (100, 50))  # Y Axis
    graph.DrawLine((0, 0), (0, 100))  # X Axis


def drawTicks():

    divisionsX = 12
    multi = int(RATE/divisionsX)
    offsetX = int(100/divisionsX)

    divisionsY = 10
    offsetY = int(100/divisionsY)

    for x in range(0, divisionsX+1):
        # print('x:', x)
        graph.DrawLine((x*offsetX, -3), (x*offsetX, 3))
        graph.DrawText(int((x*multi)), (x*offsetX, -10), color='black')

    for y in range(0, divisionsY+1):
        graph.DrawLine((-3, y*offsetY), (3, y*offsetY))


def drawAxesLabels():
    graph.DrawText('kHz', (50, 10), color='black')
    graph.DrawText('Norm Scaled AUDIO', (-5, 50), color='black', angle=90)


def drawPlot():
    # Divide horizontal axis space by data points :
    barStep = 100/CHUNK
    x_scaled = ((_VARS['audioData']/100)*GAIN)+50

    for i, x in enumerate(x_scaled):
        graph.draw_rectangle(top_left=(i*barStep, x),
                             bottom_right=(i*barStep+barStep, 50),
                             fill_color='#B6B6B6')

                             # +----|
                             # |    |
                             # |----+ <<--



def drawFFT():

    # Not the most elegant implementation but gets the job done.
    # Note that we are using rfft instead of plain fft, it uses half
    # the data from pyAudio while preserving frequencies thus improving
    # performance, you might also want to scale and normalize the fft data
    # Here I am simply using hardcoded values/variables which is not ideal.

    barStep = 100/(CHUNK/2)  # Needed to fit the data into the plot.
    fft_data = np.fft.rfft(_VARS['audioData'])  # The proper fft calculation
    fft_data = np.absolute(fft_data)  # Get rid of negatives
    #print(fft_data)

    #addition of dynamic scaling for normalization
    #max_intensity=np.max(fft_data)

    fft_data = fft_data/10000  # Constant scaled; NEED TO DYNAMICALLY SCALE IT
    #The resultant value is of scale 0 to 12 ish

    #print(fft_data)
    for i, x in enumerate(fft_data):
        graph.draw_rectangle(top_left=(i*barStep, x+50),
                             bottom_right=(i*barStep+barStep, 50),
                             fill_color='black')

# PYAUDIO STREAM :


def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Stop').Update(disabled=True)
        _VARS['window'].FindElement('Listen').Update(disabled=False)


def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # print(_VARS['audioData'])
    return (in_data, pyaudio.paContinue)

def listen():
    _VARS['window'].FindElement('Stop').Update(disabled=False)
    _VARS['window'].FindElement('Listen').Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)
    _VARS['stream'].start_stream()


def updateUI():
    # Uodate volumne meter
    _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
    # Redraw plot
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()
    drawFFT()


# INIT:
drawAxis()
drawTicks()
drawAxesLabels()

# MAIN LOOP
while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    if event == 'Listen':
        listen()
    if event == 'Stop':
        stop()
    elif _VARS['audioData'].size != 0:
        updateUI()


_VARS['window'].close()