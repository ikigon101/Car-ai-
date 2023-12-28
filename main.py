import pygame
import os
import math
import sys
import neat

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

TRACK = pygame.image.load(os.path.join("Assets", "track2.png"))


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("Assets", "car.png"))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(425, 645))
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotational_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []

    def update(self):
        self.radars.clear()
        self.drive()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        self.rotate()
        self.collide()
        self.data()

    def drive(self):
        self.rect.center += self.vel_vector *6

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotational_vel
            self.vel_vector.rotate_ip(self.rotational_vel)
        if self.direction == -1:
            self.angle += self.rotational_vel
            self.vel_vector.rotate_ip(-self.rotational_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        length = 0
        offset = 10  # Offset to start the radar line a bit away from the car
        x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * offset)
        y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * offset)

        while length < 200:
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * (length + offset))
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * (length + offset))

            if not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                break

            if SCREEN.get_at((x, y)) == pygame.Color(255, 255, 255, 255):
                break

            length += 1

        pygame.draw.line(SCREEN, (255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0), (x, y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                             + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar_data in enumerate(self.radars):
            input[i] = int(radar_data[1])
        return input

    def collide(self):
        length = 40
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        if (0 <= collision_point_right[0] < SCREEN_WIDTH and
            0 <= collision_point_right[1] < SCREEN_HEIGHT and
            SCREEN.get_at(collision_point_right) == pygame.Color(45, 103, 42)) or \
                (0 <= collision_point_left[0] < SCREEN_WIDTH and
                 0 <= collision_point_left[1] < SCREEN_HEIGHT and
                 SCREEN.get_at(collision_point_left) == pygame.Color(45, 103, 42)):
            self.alive = False

        pygame.draw.circle(SCREEN, (0, 255, 255), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255), collision_point_left, 4)


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)


def eval_gen(genomes, config):
    global cars, ge, nets

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((0, 0, 0))

        SCREEN.blit(TRACK, (0, 0))

        if len(cars) == 0:
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0

        for car in cars:
            car.draw(SCREEN)
            car.update()
        pygame.display.update()
        print(len(cars))


def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_gen, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)