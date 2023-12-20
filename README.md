# StepTracker
This is the code I used to integrate:

* RMS measurements from SigDigger's RMS inspector
* The [AzElBox](https://github.com/BatchDrake/AzElBox) dish rotor controller
* AstroPy's Sun coordinate calculations

to perform [step-tracking](http://www.antesky.com/what-are-methods-for-antenna-tracking-system/) of the Sun and calibrate the pointing model of my antenna. The code performs a diamond search near the Sun (an initial guess must be provided) to maximize the measured RMS every 10 seconds. The resulting rotor coordinates (and actual coordinates) are later dumped to a log file, from which the model is trained.
