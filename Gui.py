import PySimpleGUI as sg
import pyaudio
import numpy as np

"""Audio to Frequency plot """

# VARS CONSTS:
_VARS = {'window': False,
         'stream': False,
         'streamSecond': False,
         'audioData': np.array([]),
         'comparisonData':np.array([])}

# PySimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('Black')
FrameWidth = 1440
FrameHeight = 500
OriginX_1 = -10
OriginY_1 = -10
OriginX_2 = 60
OriginY_2 = -10
X_Axis_Length=48    #better if it is multiple of 12
Y_Axis_Length=100

#GUI layout
layout = [[sg.Graph(canvas_size=(FrameWidth, FrameHeight),
                    graph_bottom_left=(-16, -16),
                    graph_top_right=(116, 116),
                    background_color='#B9B9B9',
                    key='graph')],
          [sg.ProgressBar(4000, orientation='h',
                          size=(20, 20), key='-PROG-'),sg.Push(),sg.ProgressBar(4000, orientation='h',
                          size=(20, 20),key='-PROG2-')],
          [sg.Button('Listen', font=AppFont),
           sg.Button('Stop', font=AppFont, disabled=True),
           sg.Button('Exit', font=AppFont),sg.Push(),sg.Button('ListenAudio2',font=AppFont),
           sg.Button('StopAudio2', font=AppFont, disabled=True)]]
_VARS['window'] = sg.Window('Guitar sound visualizer',
                            layout, finalize=True)

graph = _VARS['window']['graph']

# INIT vars:
CHUNK = 128  # Samples: 1024,  512, 256, 128 <<<<<ALSO THE SIZE OF NP ARRAY
RATE = 4800  # Going quadruple the peak frequency range of standard 5 stringed acoustic guitar: 1200Hz to add harmonics
INTERVAL = 1  # Sampling Interval in Seconds ie Interval to listen
TIMEOUT = 10  # In ms for the event loop
GAIN = 10
pAud = pyaudio.PyAudio()

barStep = 100/(CHUNK)  # Needed to fit the data into the plot.
# FUNCTIONS:


def drawAxis():
    #axes 1
    graph.DrawLine((OriginX_1, 0), (X_Axis_Length, 0))  # X Axis
    graph.DrawLine((OriginX_1, 0), (OriginX_1, Y_Axis_Length))  # Y Axis

    #axes 2
    graph.DrawLine((OriginX_2, 0), (OriginX_2 + X_Axis_Length , 0))  # X Axis
    graph.DrawLine((OriginX_2, 0), (OriginX_2, Y_Axis_Length))  # Y Axis
    

def drawTicks():

    divisionsX = 12
    multi = int(RATE/divisionsX)
    offsetX = int(X_Axis_Length/divisionsX)

    divisionsY = 10
    offsetY = int(100/divisionsY)

    for x in range(0, divisionsX+1):
        # print('x:', x)
        # X-Axis ticks for graph 1
        graph.DrawLine((x*offsetX + OriginX_1, -3), (x*offsetX + OriginX_1, 3))
        graph.DrawText(int((x*multi)), (x*offsetX + OriginX_1, -10), color='black')

        # X-Axis ticks for graph 2
        graph.DrawLine((x*offsetX + OriginX_2, -3), (x*offsetX + OriginX_2, 3))
        graph.DrawText(int((x*multi)), (x*offsetX + OriginX_2, -10), color='black')

    for y in range(0, divisionsY+1):
        # X-Axis ticks for graph 1
        graph.DrawLine((-3 + OriginX_1, y*offsetY), (3 + OriginX_1, y*offsetY))

        #ticks for graph 2 
        graph.DrawLine((-3 + OriginX_2, y*offsetY), (3 + OriginX_2, y*offsetY))

def drawAxesLabels():
    graph.DrawText('Hz', (53, 0), color='black')
    graph.DrawText('Dynamically Scaled Audio 1', (-5 + OriginX_1, 50), color='black', angle=90)
    graph.DrawText('Dynamically Scaled Audio 2', (-5 + OriginX_2, 50), color='black', angle=90)


def drawPlot():
    # Divide horizontal axis space by data points :
    barStep = 100/CHUNK
    x_scaled = ((_VARS['audioData']/100)*GAIN)+50

    for i, x in enumerate(x_scaled):
        graph.draw_rectangle(top_left=(i*barStep + OriginX_1, x + OriginY_1),
                             bottom_right=(i*barStep+barStep + OriginX_1, 50 + OriginY_1),
                             fill_color='#B6B6B6')

                             # +----|
                             # |    |
                             # |----+ <<--



def drawLeftFFT():

    # Not the most elegant implementation but gets the job done.
    # Note that we are using rfft instead of plain fft, it uses half
    # the data from pyAudio while preserving frequencies thus improving
    # performance, you might also want to scale and normalize the fft data
    # Here I am simply using hardcoded values/variables which is not ideal.

   
    fft_data = np.fft.rfft(_VARS['audioData'])  # The proper fft calculation
    fft_data = np.absolute(fft_data)  # Get rid of negatives
    #print(fft_data)

    #FFT on comparison data
    

    #addition of dynamic scaling for normalization

    #fft_data = fft_data/10000  # Constant scaled; NEED TO DYNAMICALLY SCALE IT
    
    #normalizing the vector using numpy
    normalized_data=np.linalg.norm(fft_data)
    fft_data=(fft_data/normalized_data) * 100

    #print(fft_data)
    for i, x in enumerate(fft_data):
        # here the i is the index and x is the value #SHOULD JUST REMOVE FIFY AND SET THE X AXIS LOWER
        graph.draw_rectangle(top_left=(i*barStep + OriginX_1, x),
                             bottom_right=(i*barStep+barStep + OriginX_1, 0),
                             fill_color='black')

def drawRightFFT():
    
    comparison_fft = np.fft.rfft(_VARS['comparisonData'])
    comparison_fft = np.absolute(comparison_fft)

    #normalization
    normalized_data=np.linalg.norm(comparison_fft)
    comparison_fft=(comparison_fft/normalized_data) * 100

    for i, x in enumerate(comparison_fft):
        # here the i is the index and x is the value #SHOULD JUST REMOVE FIFY AND SET THE X AXIS LOWER
        graph.draw_rectangle(top_left=(i*barStep + OriginX_2, x),
                             bottom_right=(i*barStep+barStep + OriginX_2, 0),
                             fill_color='black')
# PYAUDIO STREAM :


def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window']['Stop'].Update(disabled=True)
        _VARS['window']['Listen'].Update(disabled=False)


def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # print(_VARS['audioData'])
    return (in_data, pyaudio.paContinue)

def secondCallback(in_data, frame_count, time_info, status):
    _VARS['comparisonData'] = np.frombuffer(in_data,dtype=np.int16)
    return (in_data,pyaudio.paContinue)

def listen():
    _VARS['window']['Stop'].Update(disabled=False)
    _VARS['window']['Listen'].Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)
    _VARS['stream'].start_stream()

#second stream

def compare():
    _VARS['window']['StopAudio2'].Update(disabled=False)
    _VARS['window']['ListenAudio2'].Update(disabled=True)
    _VARS['streamSecond']=pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=secondCallback)
    _VARS['streamSecond'].start_stream()

def stopCompareStream():
    if _VARS['streamSecond']:
        _VARS['streamSecond'].stop_stream()
        _VARS['streamSecond'].close()
        _VARS['window']['-PROG2-'].update(0)    #another variable not initialized
        _VARS['window']['StopAudio2'].Update(disabled=True)
        _VARS['window']['ListenAudio2'].Update(disabled=False)

def updateLeftUI():
    # Update volume meter
    _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
    
    
    # Redraw plot
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()
    drawLeftFFT()
    #drawleftFFT was here
    

def updateRightUI():
    #right progress bar
    _VARS['window']['-PROG2-'].update(np.amax(_VARS['comparisonData']))

    #Redraw plot
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()
    drawRightFFT()

def updateBothUI():
     #right progress bar
    _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
    _VARS['window']['-PROG2-'].update(np.amax(_VARS['comparisonData']))

    #Redraw plot
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()
    drawLeftFFT()
    drawRightFFT()



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
    if event == 'ListenAudio2':
        compare()
    if event == 'StopAudio2':
        stopCompareStream()
    if event == 'Listen':
        listen()
    if event == 'Stop':
        stop()
    if _VARS['comparisonData'].size !=0 and  _VARS['audioData'].size == 0 :
        updateRightUI()
    elif _VARS['audioData'].size != 0 and _VARS['comparisonData'].size ==0:
       updateLeftUI()
    elif _VARS['audioData'].size != 0 and _VARS['comparisonData'].size !=0:
        updateBothUI()


       #flickering problem due to the progressbar being updated same time as the graph

    


_VARS['window'].close()