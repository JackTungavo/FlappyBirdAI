##Modules Installed:
##    *numpy        --COMPLETE
##    *pygame       --COMPLETE
##    *neat-python  --COMPLETE
##    *graphviz     --COMPLETE
##    *matplotlib   --COMPLETE

import random
import time
import os
import pickle
import pygame
import neat

WindowWidth = 600
WindowHeight = 800
Floor = 730
IsDrawingLines = False

WIN = pygame.display.set_mode((WindowWidth, WindowHeight))
pygame.font.init()
StatFont = pygame.font.SysFont("arial", 50)
EndFont = pygame.font.SysFont("arial", 70)
pygame.display.set_caption("Flappy Bird")

PipeImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
BackgroundImage = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
BirdImages = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
BaseImage = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

AmountToGenerate = 30
NumberGen = 0
IsUnlimited = True

##CLASSES
class Bird:                     ##Blueprint for Bird Object
    MaximumRotation = 25
    RotationVelocity = 20
    AnimTime = 5                ##How Long It Takes To Complete Animation

    def __init__(self, x, y):   ##Constructor for Bird, x:IsA(integer), y:IsA(integer)
        self.x = x
        self.y = y
        self.tilt = 0           ##Initial Bird Tilt
        self.tick = 0           ##Measuring Time using Tick
        self.vel = 0            ##Initial Bird Velocity
        self.height = self.y
        self.AnimKeyframeIndex = 0
        self.img = BirdImages[0]
    ##end

    def jump(self):             ##Procedure To Make Bird Jump
        self.vel = -10.5
        self.tick = 0
        self.height = self.y
    ##end

    def move(self):
        self.tick = self.tick + 1
        
        ##CalculateHowFastBirdDrops
        displacement = self.vel*(self.tick) + 0.5*(3)*(self.tick)**2 ##Get Displacement
        if displacement >= 16: displacement = (displacement/abs(displacement)) * 16     ##Getting Terminal Vel
        if displacement < 0: displacement = displacement - 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:   ##Downwards
            if self.tilt < self.MaximumRotation: self.tilt = self.MaximumRotation
        else:                                               ##Upwards
            if self.tilt > -90: self.tilt = self.tilt - self.RotationVelocity
        ##end
    ##end

    def draw(self, win):        ##PlacingBird
        self.AnimKeyframeIndex = self.AnimKeyframeIndex + 1

        ##CreatingLoopToGoThroughImagesToAnimateBird
        if self.AnimKeyframeIndex <= self.AnimTime:
            self.img = BirdImages[0]
        elif self.AnimKeyframeIndex <= self.AnimTime*2:
            self.img = BirdImages[1]
        elif self.AnimKeyframeIndex <= self.AnimTime*3:
            self.img = BirdImages[2]
        elif self.AnimKeyframeIndex <= self.AnimTime*4:
            self.img = BirdImages[1]
        elif self.AnimKeyframeIndex == self.AnimTime*4 + 1:
            self.img = BirdImages[0]
            self.AnimKeyframeIndex = 0
        ##end

        ##WhenFalling,ItIsNotDoingAnimation
        if self.tilt <= -80:
            self.img = BirdImages[1]
            self.img_count = self.AnimTime*2
        ##end

        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)##RotateBird
    ##end

    def get_mask(self):     ##ReturnBirdImagesMaskForBirdForCollisionCalculation
        return pygame.mask.from_surface(self.img)
    ##end
##end

class Pipe():                       ##Object Blueprint for All Pipes in Window
    GAP = 200
    VEL = 5

    def __init__(self, x):          ##Constructor for Pipe Object, x:IsA(integer), y:IsA(Integer)
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.TopOfPipe = pygame.transform.flip(PipeImage, False, True)
        self.BottomOfPipe = PipeImage
        self.passed = False
        self.set_height()
    ##end

    def set_height(self):           ##Randomizing Height Of Pipe
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TopOfPipe.get_height()
        self.bottom = self.height + self.GAP
    ##end

    def move(self):                 ##Move Pipe
        self.x = self.x - self.VEL
    ##end

    def draw(self, win):            ##Place Pipe in Window
        win.blit(self.TopOfPipe, (self.x, self.top))
        win.blit(self.BottomOfPipe, (self.x, self.bottom))
    ##end

    def collide(self, bird, win):   ##Checking If Object Is Hitting Pipe, Bird:IsA(BirdObject)
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TopOfPipe)
        bottom_mask = pygame.mask.from_surface(self.BottomOfPipe)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True
        else:
            return False
        ##end
    ##end
##end

class Base:                         ##Base for Making Floor Move
    VEL = 5
    WIDTH = BaseImage.get_width()
    IMG = BaseImage

    def __init__(self, y):          ##Constructor, y:IsA(Integer)
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    ##end
        
    def move(self):                 ##Procedure to Move Floor
        self.x1 = self.x1 - self.VEL
        self.x2 = self.x2 - self.VEL
        if self.x1 + self.WIDTH < 0: self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0: self.x2 = self.x1 + self.WIDTH
    ##end

    def draw(self, win):            ##Place Floors, win:IsA(Pygame Window)
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
    ##end
##end

##PROCEDURES##
def blitRotateCenter(surf, image, topleft, angle):
    ##CausingASpriteWithinPyGametoRotate, surf:IsA(surface), image:IsA(Image), topLeft:IsA(TopLeftPosOfImage), angle:IsA(float), returns None
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)
##end

def draw_window(win, birds, pipes, base, score, NumberGen, pipe_ind):
    ##PlacingAllObjectsToBeSetWithinTheWindow, win:IsA(PyGameWindow. Birds:IsA(list of bird objects), pipes:IsA(list of all pipe objects), NumberGen:IsA(integer -> generation number), pipe_ind:IsA(Int -> ClosestPipe))
    if NumberGen == 0:  NumberGen = 1
    win.blit(BackgroundImage, (0,0))
    for pipe in pipes:  pipe.draw(win)

    base.draw(win)
    for bird in birds:  ##GettingLinesFromBirdToPipe
        if IsDrawingLines:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].TopOfPipe.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].BottomOfPipe.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
            ##end
        ##end
        bird.draw(win)  ###PlacingBirds
    ##end

    ## Placing Score Display
    score_label = StatFont.render("CurrentScore:" + str(score),1,(231,225,218))
    win.blit(score_label, (WindowWidth - score_label.get_width() - 15, 10))

    ## Placing Number of Birds Alive Display
    score_label = StatFont.render("BirdsAlive: " + str(len(birds)),1,(231,225,218))
    win.blit(score_label, (10, 50))

    ## Placing Generation Display
    score_label = StatFont.render("Gens: " + str(NumberGen-1),1,(231,225,218))
    win.blit(score_label, (10, 10))

    pygame.display.update()
##end

def eval_genomes(genomes, config):      ##MainSimulation
    global WIN, NumberGen
    win = WIN
    NumberGen = NumberGen + 1

    nets = []                                           ##Stores Neural Network
    birds = []                                          ##Stores Bird Objects
    ge = []                                             ##Stores Genomes
    for genome_id, genome in genomes:                   ##GenomeIndex,GenomeObject
        genome.fitness = 0                              ##Initialise Fitness Level To 0, Represent How Far Bird Goes
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)
    ##end

    ##Initialising Main Game Variables
    base = Base(Floor)                       ##Constructing Floor Object
    pipes = [Pipe(700)]                       ##Storing List of All Pipes, While Sending Start Position Of Pipe
    score = 0                                     ##Initialising Score to 0
    clock = pygame.time.Clock()         ##Placing Clock In A Variable to Improve Code Readablility
    
    run = True
    while run and len(birds) > 0:           ##MainGameLoop
        clock.tick(30)                            ##Stops Game Running at More than 30 FPS
        for event in pygame.event.get():   ##Connecting Quit Event Check Whether Player Is Quitting Game
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
            ##end
        ##end

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TopOfPipe.get_width():  ## Using Second or First?
                pipe_ind = 1                                                                                           ## Index of Current On Screen Pipe 
            ##end
        ##end
                
        for x, bird in enumerate(birds):  ## Reward Bird "0.1" Fitness for Every Frame It Is Not Dead
            ge[x].fitness = ge[x].fitness + 0.1
            bird.move()

            #'#Input Bird Location, TopOfPipe Positio, BottomOfPipe Position, and Gets Signal to Jump
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5: bird.jump()
        ##end

        base.move() ##MoveFloor

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            for bird in birds:  ##CollisionCheckForEveryBird
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness = ge[birds.index(bird)].fitness - 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))
                ##end
            ##end

            if pipe.x + pipe.TopOfPipe.get_width() < 0: rem.append(pipe)    ##AddToListofObjectsToDestroy
            if not pipe.passed and pipe.x < bird.x:                                     ##AddNewPipeOnceBirdHasTravelledPassedPipe
                pipe.passed = True
                add_pipe = True
            ##end
        ##end

        if add_pipe:    ##ConfirmationThatBirdHasPassedPipe, So Can Increase Score & Fitness
            score = score + 1
            for genome in ge: genome.fitness = genome.fitness + 5
            pipes.append(Pipe(WindowWidth))
        ##end

        for r in rem: pipes.remove(r)   ##RemoveAllPipeObjectsInRemoveList

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= Floor or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
            ##end
        ##end

        draw_window(WIN, birds, pipes, base, score, NumberGen, pipe_ind)    ##RePlaceAllOnScreenAssets

        if (IsUnlimited == False) and (score > 20):              ##StopsIfNotUnlimited&GetsToASuitableScore
            pickle.dump(nets[0],open("best.pickle", "wb"))  ##WriteToBinaryFileWith"(wb)", AsPickleWritesObjectInByteStreamForm
            break
        ##end
##end

def run(config_file):
    ##Get "NEAT" algroithm configurations from the text file.
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_file)

    ## Get Population To Use For NEAT
    p = neat.Population(config)

    ## Get Reporter to Show Results in Output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    ## Number of Times to Run from "AmountTOGenerate" Variable.
    winner = p.run(eval_genomes, AmountToGenerate)
    
    ## Output Stats
    print('\nBest genome:\n{!s}'.format(winner))
##end

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    run(os.path.join(local_dir, 'config-feedforward.txt'))
