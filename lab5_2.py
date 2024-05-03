import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Button, CheckboxGroup, Select
from bokeh.plotting import figure
from scipy.signal import butter, lfilter

""" Launch bokeh ==> bokeh serve --show lab5_2.py """

# Function to generate harmonic signal
def generateHarmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2*np.pi*frequency*t + phase)

# Function to generate noise
def generateNoise(t, noiseMean, noiseCovariance):
    return np.random.normal(noiseMean, np.sqrt(noiseCovariance), len(t))

# Function to combine signal and noise
noiseGlobal = None
noiseGlobalMean = None
noiseGlobalCovariance = None

def harmonicWithNoise(t, amplitude, frequency, phase, noiseMean, noiseCovariance, showNoise, noise=None):
    global noiseGlobal, noiseGlobalMean, noiseGlobalCovariance
    harmonicSignal = generateHarmonic(t, amplitude, frequency, phase)
    if noise is not None:
        return harmonicSignal + noise
    else:
        if noiseGlobal is None or len(noiseGlobal)!=len(t) or noiseMean != noiseGlobalMean or noiseCovariance != noiseGlobalCovariance:
            noiseGlobal = generateNoise(t, noiseMean, noiseCovariance)
            noiseGlobalMean = noiseMean
            noiseGlobalCovariance = noiseCovariance
        if showNoise:
            return harmonicSignal + noiseGlobal
        else:
            return harmonicSignal

# Function to filter signal
def lowpassFilter(signal, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normalCutoff = cutoff/nyquist
    b, a = butter(order, normalCutoff, btype='low', analog=False)
    return lfilter(b, a, signal)

# Initial parameters
initialAmplitude = 1.0
initialFrequency = 1.0
initialPhase = 0.0
initialNoiseMean = 0.0
initialNoiseCovariance = 0.1
initialCutoffFrequency = 1.0

t = np.arange(0.0, 10.0, 0.01)
samplingFrequency = len(t) / (t[-1] - t[0])
signal = harmonicWithNoise(t, initialAmplitude, initialFrequency,
                           initialPhase, initialNoiseMean,
                           initialNoiseCovariance, True)
filteredSignal = lowpassFilter(signal, initialCutoffFrequency, samplingFrequency)

source = ColumnDataSource(data=dict(t=t, signal=signal, filteredSignal=filteredSignal))
plot = figure(title="Graph of Harmonic with Noise", height=300, width=600, y_range=(-3, 3))
line = plot.line('t', 'signal', source=source, line_width=3, line_alpha=0.6, color='green')
scatter = plot.scatter('t', 'signal', source=source, size=3, color='green', alpha=0.6, visible=False)

plotFiltered = figure(title="Filtered Harmonic", height=300, width=600, y_range=(-3, 3))
lineFiltered = plotFiltered.line('t', 'filteredSignal', source=source, line_width=3, line_alpha=0.6, color='purple')
scatterFiltered = plotFiltered.scatter('t', 'filteredSignal', source=source, size=3, color='purple', alpha=0.6, visible=False)
amplitudeSlider = Slider(start=0.1, end=10.0, value=initialAmplitude, step=0.1, title="Amplitude", bar_color='yellow')
frequencySlider = Slider(start=0.1, end=10.0, value=initialFrequency, step=0.1, title="Frequency", bar_color='yellow')
phaseSlider = Slider(start=0, end=2*np.pi, value=initialPhase, step=0.1, title="Phase", bar_color='yellow')
noiseMeanSlider = Slider(start=-1.0, end=1.0, value=initialNoiseMean, step=0.1, title="Noise Mean", bar_color='yellow')
noiseCovarianceSlider = Slider(start=0.0, end=1.0, value=initialNoiseCovariance, step=0.01, title="Noise Covariance", bar_color='yellow')
cutoffSlider = Slider(start=0.1, end=5.0, value=initialCutoffFrequency, step=0.1, title="Cutoff Frequency", bar_color='yellow')

showNoiseCheckbox = CheckboxGroup(labels=["Show Noise"], active=[0])

# Dropdown menu to choose the plot type
plotTypeSelect = Select(title="Plot Type:", value="Line", options=["Line", "Scatter"])

def updateData(attrname, old, new):
    # Update data
    newSignal = harmonicWithNoise(t, amplitudeSlider.value, frequencySlider.value,
                                  phaseSlider.value, noiseMeanSlider.value, noiseCovarianceSlider.value,
                                  0 in showNoiseCheckbox.active)
    newFilteredSignal = lowpassFilter(newSignal, cutoffSlider.value, samplingFrequency)
    source.data = dict(t=t, signal=newSignal, filteredSignal=newFilteredSignal)
    
    # Update plot type
    if plotTypeSelect.value == "Line":
        line.visible = True
        scatter.visible = False
        lineFiltered.visible = True
        scatterFiltered.visible = False
    elif plotTypeSelect.value == "Scatter":
        line.visible = False
        scatter.visible = True
        lineFiltered.visible = False
        scatterFiltered.visible = True

for widget in [amplitudeSlider, frequencySlider, phaseSlider, noiseMeanSlider, noiseCovarianceSlider, cutoffSlider]:
    widget.on_change('value', updateData)

def showNoiseCheckboxChanged(attrname, old, new):
    updateData(None, None, None)

showNoiseCheckbox.on_change('active', showNoiseCheckboxChanged)
resetButton = Button(label="Reset", button_type="success", width=100)

def reset():
    amplitudeSlider.value = initialAmplitude
    frequencySlider.value = initialFrequency
    phaseSlider.value = initialPhase
    noiseMeanSlider.value = initialNoiseMean
    noiseCovarianceSlider.value = initialNoiseCovariance
    cutoffSlider.value = initialCutoffFrequency
    global noiseGlobal, noiseGlobalMean, noiseGlobalCovariance
    noiseGlobal = None
    noiseGlobalMean = None
    noiseGlobalCovariance = None
    updateData(None, None, None)

resetButton.on_click(reset)
controls = column(amplitudeSlider, frequencySlider,
                  phaseSlider, noiseMeanSlider,
                  noiseCovarianceSlider, cutoffSlider,
                  showNoiseCheckbox, resetButton,
                  plotTypeSelect)

curdoc().add_root(row(column(plot, plotFiltered), controls))
curdoc().title = "Harmonic with Noise and Filtering"