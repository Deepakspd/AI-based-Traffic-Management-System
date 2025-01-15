import pygame
import random
import threading
import time
import os
import sys

# Initialize Pygame
pygame.init()

# Global variables
currentGreen = 0
currentYellow = 0
nextGreen = 1
timeElapsed = 0
simTime = 60  # total simulation time in seconds
defaultGreen = 10
defaultYellow = 3
defaultRed = 10
signals = []
vehicles = {}
directionNumbers = [0, 1, 2, 3]
vehicleCountTexts = ["0", "0", "0", "0"]
signalCoods = [(100, 50), (300, 50), (500, 50), (700, 50)]
signalTimerCoods = [(100, 150), (300, 150), (500, 150), (700, 150)]
vehicleCountCoods = [(100, 200), (300, 200), (500, 200), (700, 200)]
noOfSignals = 4

# Vehicle class
class Vehicle:
    def __init__(self, lane, vehicle_type, direction, direction_number, will_turn):
        self.lane = lane
        self.type = vehicle_type
        self.direction = direction
        self.direction_number = direction_number
        self.will_turn = will_turn
        self.x = 0
        self.y = lane * 100
        self.currentImage = pygame.image.load(f'images/vehicles/{vehicle_type}.png')

    def move(self):
        # Simple logic to move vehicles
        self.x += 2  # Move right
        if self.x > 1400:
            vehicles[directionNumbers[self.direction]].append(self)

# Signal class
class Signal:
    def __init__(self, green, yellow, red):
        self.green = green
        self.yellow = yellow
        self.red = red
        self.signalText = ""

# Initialize signals and vehicles
def initialize():
    global signals
    for _ in range(noOfSignals):
        signals.append(Signal(defaultGreen, defaultYellow, defaultRed))
    for i in range(noOfSignals):
        vehicles[i] = {'crossed': 0}

def load_assets():
    global redSignal, yellowSignal, greenSignal, background
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    background = pygame.image.load('images/mod_int.png')
    pygame.mixer.music.load('sounds/background.mp3')
    pygame.mixer.music.play(-1)

def repeat():
    global currentGreen, currentYellow, nextGreen
    while signals[currentGreen].green > 0:
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"
    for i in range(3):
        for vehicle in vehicles[directionNumbers[currentGreen]]:
            vehicle.x = 0  # Reset vehicle positions

    while signals[currentGreen].yellow > 0:
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0

    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
       
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()

def printStatus():
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                print("GREEN TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
            else:
                print("YELLOW TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
        else:
            print("RED TS", i + 1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
    print()

def updateValues():
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 4)
        lane_number = 0 if vehicle_type == 4 else random.randint(1, 2)
        will_turn = random.choice([0, 1]) if lane_number == 2 else 0
        direction_number = random.choices(directionNumbers, weights=[0.4, 0.3, 0.2, 0.1])[0]
        Vehicle(lane_number, vehicle_type, direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)

def simulationTime():
    global timeElapsed
    while True:
        timeElapsed += 1
        time.sleep(1)
        if timeElapsed >= simTime:
            totalVehicles = sum(vehicles[i]['crossed'] for i in range(noOfSignals))
            print('Total vehicles passed:', totalVehicles)
            print('Total time passed:', timeElapsed)
            print('Vehicles passed per unit time:', totalVehicles / timeElapsed)
            os._exit(1)

class Main:
    def __init__(self):
        threading.Thread(target=simulationTime, daemon=True).start()
        threading.Thread(target=initialize, daemon=True).start()
        load_assets()
        self.run()

    def run(self):
        screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption("Traffic Simulation")
        font = pygame.font.Font(None, 30)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.blit(background, (0, 0))
            for i in range(noOfSignals):
                if i == currentGreen:
                    signal_image = yellowSignal if currentYellow else greenSignal
                else:
                    signal_image = redSignal
                screen.blit(signal_image, signalCoods[i])
                
                # Display signal timers
                signal_text = font.render(str(signals[i].green if i == currentGreen else signals[i].red), True, (255, 255, 255))
                screen.blit(signal_text, signalTimerCoods[i])
                
                # Display vehicle count
                vehicle_count_text = font.render(str(vehicles[directionNumbers[i]]['crossed']), True, (0, 0, 0))
                screen.blit(vehicle_count_text, vehicleCountCoods[i])

            pygame.display.update()

if __name__ == "__main__":
    Main()
