from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import filtfilt, iirfilter

# Function to generate a harmonic signal
def generateHarmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2*np.pi*frequency*t + phase) # formule

# Function to generate noise
def generateNoise(t, noiseMean, noiseCovariance):
    return np.random.normal(noiseMean, np.sqrt(noiseCovariance), len(t))

# Function to add noise to signal
def addNoiseToSignal(t, amplitude, frequency, phase, noiseMean, noiseCovariance, showNoise, customNoise=None):
    signal = generateHarmonic(t, amplitude, frequency, phase)
    if customNoise is not None:
        return signal + customNoise
    else:
        noise = generateNoise(t, noiseMean, noiseCovariance)
        if showNoise:
            return signal + noise
        else:
            return signal

# Function to apply low-pass filter to signal
def applyLowPassFilter(signal, cutoffFrequency, samplingFrequency, filterOrder=5):
    b, a = iirfilter(filterOrder, cutoffFrequency / (0.5 * samplingFrequency), btype='low', ftype='butter')
    filteredSignal = filtfilt(b, a, signal)
    return filteredSignal

# Default parameters
initialAmplitude = 1.0
initialFrequency = 1.0
initialPhase = 0.0
initialNoiseMean = 0.0
initialNoiseCovariance = 0.1
initialCutoffFrequency = 1.0

t = np.arange(0.0, 10.0, 0.01)
samplingFrequency = len(t) / (t[-1] - t[0])

fig, ax = plt.subplots(2, figsize=(8, 6))
plt.subplots_adjust(left=0.1, bottom=0.4, hspace=0.5)

# Initial plot of signals
ax[0].set_title('Harmonic Signal with Noise')
harmonicLine, = ax[0].plot(t, generateHarmonic(t, initialAmplitude, initialFrequency, initialPhase), lw=2, color='red')
withNoiseLine, = ax[0].plot(t, addNoiseToSignal(t, initialAmplitude, initialFrequency, initialPhase, initialNoiseMean, initialNoiseCovariance, True), lw=2, color='red')
ax[1].set_title('Filtered Harmonic Signal')
filteredLine, = ax[1].plot(t, addNoiseToSignal(t, initialAmplitude, initialFrequency, initialPhase, initialNoiseMean, initialNoiseCovariance, True), lw=2, color='blue')

axColor = 'lightblue'
axAmplitude = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axColor)
axFrequency = plt.axes([0.1, 0.15, 0.65, 0.03], facecolor=axColor)
axPhase = plt.axes([0.1, 0.2, 0.65, 0.03], facecolor=axColor)
axNoiseMean = plt.axes([0.1, 0.05, 0.65, 0.03], facecolor=axColor)
axNoiseCovariance = plt.axes([0.1, 0.0, 0.65, 0.03], facecolor=axColor)
axCutoffFrequency = plt.axes([0.1, 0.25, 0.65, 0.03], facecolor=axColor)
sliderAmplitude = Slider(axAmplitude, 'Amplitude', 0.1, 10.0, valinit=initialAmplitude, color='purple')
sliderFrequency = Slider(axFrequency, 'Frequency', 0.1, 10.0, valinit=initialFrequency, color='green')
sliderPhase = Slider(axPhase, 'Phase', 0.0, 2 * np.pi, valinit=initialPhase, color='orange')
sliderNoiseMean = Slider(axNoiseMean, 'Noise Mean', -1.0, 1.0, valinit=initialNoiseMean, color='red')
sliderNoiseCovariance = Slider(axNoiseCovariance, 'Noise Covariance', 0.0, 1.0, valinit=initialNoiseCovariance, color='blue')
sliderCutoffFrequency = Slider(axCutoffFrequency, 'Cutoff Frequency', 0.1, 5.0, valinit=initialCutoffFrequency, color='yellow')

# Function to update the plot
def updatePlot(val):
    amplitude = sliderAmplitude.val
    frequency = sliderFrequency.val
    phase = sliderPhase.val
    noiseMean = sliderNoiseMean.val
    noiseCovariance = sliderNoiseCovariance.val
    showNoise = cbShowNoise.get_status()[0]
    harmonicLine.set_ydata(generateHarmonic(t, amplitude, frequency, phase))
    withNoiseLine.set_ydata(addNoiseToSignal(t, amplitude, frequency, phase, noiseMean, noiseCovariance, showNoise))
    cutoffFrequency = sliderCutoffFrequency.val
    filteredSignal = applyLowPassFilter(withNoiseLine.get_ydata(), cutoffFrequency, samplingFrequency)
    filteredLine.set_ydata(filteredSignal)
    fig.canvas.draw_idle()

# Assign update function to sliders
sliderAmplitude.on_changed(updatePlot)
sliderFrequency.on_changed(updatePlot)
sliderPhase.on_changed(updatePlot)
sliderNoiseMean.on_changed(updatePlot)
sliderNoiseCovariance.on_changed(updatePlot)
sliderCutoffFrequency.on_changed(updatePlot)

# Add checkbox for showing/hiding noise
checkboxAx = plt.axes([0.87, 0.1, 0.1, 0.07], facecolor=axColor)
cbShowNoise = CheckButtons(checkboxAx, ('Show Noise',), (True,))
cbShowNoise.on_clicked(updatePlot)

# Add button to reset parameters
resetAx = plt.axes([0.87, 0.025, 0.1, 0.07])
resetButton = Button(resetAx, 'Reset', color=axColor, hovercolor='0.975')

def resetParameters(event):
    sliderAmplitude.reset()
    sliderFrequency.reset()
    sliderPhase.reset()
    sliderNoiseMean.reset()
    sliderNoiseCovariance.reset()
    sliderCutoffFrequency.reset()
    updatePlot(None)

resetButton.on_clicked(resetParameters)
plt.show()