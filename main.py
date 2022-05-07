# Importing modules.
import pygame  # The module for creating the base game.
import random
import neat
import os
import math

pygame.init()  # Initializing the pygame module.


# Function for getting the distance between two points
def get_distance(a_position, b_position):
    horizontal_distance = a_position[0] - b_position[0]
    vertical_distance = a_position[1] - b_position[1]
    return math.sqrt(math.pow(horizontal_distance, 2) + math.pow(vertical_distance, 2))


WIDTH, HEIGHT = 1100, 500  # Defining the size of the screen.
CANVAS = pygame.display.set_mode((WIDTH, HEIGHT))  # Creating the canvas.
BACKGROUND = pygame.image.load('assets/background.png').convert_alpha()  # The background image

clock = pygame.time.Clock()  # Creating a clock.

running = True  # This variable will check if the game is running or not.

game_score = 0  # The score
game_speed = 8  # The game speed

# Player settings


class Cat:
    def __init__(self, image_right, image_left, image_down):
        self.WIDTH, self.HEIGHT = 60, 90  # Dimensions of the cat
        self.HORIZONTAL, self.vertical = 110, (HEIGHT - self.HEIGHT) - 40  # Its positions
        self.velocity = 16  # Velocity (used when jumping)
        self.is_jumping = False  # Checking if the cat is jumping
        self.is_standing_down = False  # Checking if the cat is standing down
        self.is_alive = True  # Checking if the cat is alive
        self.rectangle = pygame.Rect((self.HORIZONTAL, self.vertical), (self.WIDTH, self.HEIGHT))  # Cat's rectangle

        # Cat images (right and left are used for animating the cat walking, down when it is standing down).
        self.IMAGE_RIGHT = pygame.image.load(image_right).convert_alpha()
        self.IMAGE_LEFT = pygame.image.load(image_left).convert_alpha()
        self.IMAGE_DOWN = pygame.image.load(image_down).convert_alpha()
        self.right_or_left = 1  # Boolean for animating the cat movement

    def run(self):

        # Jumping physics
        if self.is_jumping:
            self.vertical -= self.velocity
            self.velocity -= 1
            if self.vertical >= (HEIGHT - self.HEIGHT) - 40:
                self.is_jumping = False
                self.velocity = 16

        # Defining the rectangle (it's like a hit box)
        if self.is_standing_down is False:
            self.rectangle = pygame.Rect((self.HORIZONTAL, self.vertical), (self.WIDTH, self.HEIGHT))
        else:
            self.rectangle = pygame.Rect((self.HORIZONTAL, self.vertical + (self.HEIGHT / 2)),
                                         (self.WIDTH, self.HEIGHT / 2))

        # Checking if the game score is divisible by 16 will change the walking sprite, thus creating an illusion
        # that the cat is walking.
        if game_score % 16 == 0:
            self.right_or_left *= -1

        # Displaying the cat on the screen
        if self.is_standing_down is False:
            if self.right_or_left == 1:
                CANVAS.blit(self.IMAGE_RIGHT, (self.HORIZONTAL, self.vertical))
            else:
                CANVAS.blit(self.IMAGE_LEFT, (self.HORIZONTAL, self.vertical))
        else:
            CANVAS.blit(self.IMAGE_DOWN, (self.HORIZONTAL, self.vertical + (self.HEIGHT/2)))


# List of images
images = [['assets/cat_orange_zero.png', 'assets/cat_orange_one.png', 'assets/cat_orange_down.png'],
          ['assets/cat_blue_zero.png', 'assets/cat_blue_one.png', 'assets/cat_blue_down.png'],
          ['assets/cat_red_zero.png', 'assets/cat_red_one.png', 'assets/cat_red_down.png'],
          ['assets/cat_yellow_zero.png', 'assets/cat_yellow_one.png', 'assets/cat_yellow_down.png'],
          ['assets/cat_purple_zero.png', 'assets/cat_purple_one.png', 'assets/cat_purple_down.png'],
          ['assets/cat_green_zero.png', 'assets/cat_green_one.png', 'assets/cat_green_down.png']]
# Obstacles settings
obstacles = list()


class Obstacle:
    def __init__(self, type_of_obstacle):
        self.type = type_of_obstacle  # There will be 4 types: 3 land obstacles, and a flying one.
        # Defining the dimensions and image based on the type.
        if self.type == 0:
            self.WIDTH, self.HEIGHT = 35, 70
            self.IMAGE = pygame.image.load('assets/tree_small.png').convert_alpha()
        elif self.type == 1:
            self.WIDTH, self.HEIGHT = 50, 100
            self.IMAGE = pygame.image.load('assets/tree_large.png').convert_alpha()
        elif self.type == 2:
            self.WIDTH, self.HEIGHT = 105, 70
            self.IMAGE = pygame.image.load('assets/bush.png').convert_alpha()
        elif self.type == 3:
            self.WIDTH, self.HEIGHT = 60, 50
            self.IMAGE = pygame.image.load('assets/bat.png').convert_alpha()

        if self.type == 3:
            self.horizontal, self.VERTICAL = 1200, (HEIGHT - self.HEIGHT) - 125  # The obstacle's position.
        else:
            self.horizontal, self.VERTICAL = 1200, (HEIGHT - self.HEIGHT) - 40

        self.rectangle = pygame.Rect((self.horizontal, self.VERTICAL), (self.WIDTH, self.HEIGHT))  # Its rectangle.

    # While the obstacle is running.
    def run(self):
        self.horizontal -= game_speed  # Its horizontal position is subtracted by the game speed.
        # Delete an useless obstacle.
        if self.horizontal < -self.WIDTH:
            obstacles.pop()
        self.rectangle = pygame.Rect((self.horizontal, self.VERTICAL), (self.WIDTH, self.HEIGHT))
        CANVAS.blit(self.IMAGE, (self.horizontal, self.VERTICAL))  # Drawing the obstacle.

ticking = 1
# Main function of the game
def eval_genomes(genomes, config):
    global running, game_score, game_speed, ticking
    players = list()  # List of players
    ge = list()  # List of genomes
    nets = list()  # List of nets

    # Adding the cats in the list.
    for genome_id, genome in genomes:
        color = random.randint(0, 5)  # Defining the color
        players.append(Cat(images[color][0], images[color][1], images[color][2]))  # Adding the cat
        ge.append(genome)  # Adding the genome
        # Adding the  net
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0  # Initializing its fitness.

    # While the game is running:
    while running:
        CANVAS.blit(BACKGROUND, (0, 0))

        # This will change the game speed based on the game score.
        if game_score % 100 == 0 and game_score >= 100:
            game_speed += 0.5

        for event in pygame.event.get():  # Check for inputs by the user.
            if event.type == pygame.QUIT:  # If the user quits the game.
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ticking *= -1

        # Generating the obstacles.
        if len(obstacles) == 0:
            obstacles.append(Obstacle(random.randint(0, 3)))

        # Initializing the players
        for player in players:
            player.run()

        # Initializing te obstacles
        for obstacle in obstacles:
            obstacle.run()
            for i, player in enumerate(players):
                if pygame.Rect.colliderect(obstacle.rectangle, player.rectangle):  # Check for collisions
                    ge[i].fitness -= 1  # Punishing those who hit on an obstacle
                    # Deleting them from the lists
                    players.pop(i)
                    ge.pop(i)
                    nets.pop(i)
                else:
                    ge[i].fitness += 1  # Praising the ones who don't hit on an obstacle

        for i, player in enumerate(players):
            # Adding the inputs of the neural network.
            if len(obstacles) != 0:
                output = nets[i].activate((player.rectangle.y,
                                           get_distance((player.rectangle.x, player.rectangle.y),
                                                        obstacles[0].rectangle.midtop),
                                           game_speed, obstacles[0].HEIGHT, obstacles[0].WIDTH,
                                           HEIGHT - (obstacles[0].VERTICAL + obstacles[0].HEIGHT + 40)))

            # Triggering the outputs
            if output[0] > 0.5 and player.is_standing_down is False:
                player.is_jumping = True

            if output[1] > 0.5 and player.is_jumping is False:
                player.is_standing_down = True
            else:
                player.is_standing_down = False

        if len(players) == 0:
            print(f'DEAD!, {game_score}, {game_speed}')  # Printing some data
            obstacles.pop()  # Deleting the obstacle
            # Setting everything to default.
            game_score = 0
            game_speed = 8
            break
        else:
            game_score += 1  # Adding one more for the game score
    
        if ticking == 1:
            clock.tick(60)  # Limiting the FPS
        else:
            pass
        pygame.display.update()  # Updating the canvas.


# Setup NEAT
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
            )

    pop = neat.Population(config)
    pop.run(eval_genomes, 100)


# Running the script
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
