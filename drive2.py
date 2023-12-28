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
        self.drive_state = False
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotational_vel = 5
        self.direction = 0

    def update(self):
        self.drive()
        self.rotate()
        self.radar()

    def drive(self):
        if self.drive_state:
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

    def radar(self):
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        while not SCREEN.get_at((x, y)) == pygame.Color(255, 255, 255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle)) * length)

        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

car = pygame.sprite.GroupSingle(Car())


def eval_gen():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.blit(TRACK, (0, 0))

        user_input = pygame.key.get_pressed()
        if(sum(pygame.key.get_pressed())) <= 1:
            car.sprite.drive_state = False
            car.sprite.direction = 0

        if user_input[pygame.K_UP]:
            car.sprite.drive_state = True

        if user_input[pygame.K_RIGHT]:
            car.sprite.direction = 1

        if user_input[pygame.K_LEFT]:
            car.sprite.direction = -1

        car.draw(SCREEN)
        car.update()
        pygame.display.update()


eval_gen()
