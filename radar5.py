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
        self.alive = True

    def update(self):
        self.drive()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        self.rotate()
        self.collide()

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

    def collide(self):
        length = 40
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        if SCREEN.get_at(collision_point_right) == pygame.Color(45, 103, 42) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(45, 103, 42):
            self.alive = False
            print("car died")

        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)



car = pygame.sprite.GroupSingle(Car())


def eval_gen():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen with a background color
        SCREEN.fill((0, 0, 0))

        # Draw the track image
        SCREEN.blit(TRACK, (0, 0))

        # Process user input
        user_input = pygame.key.get_pressed()
        if sum(user_input) <= 1:
            car.sprite.drive_state = False
            car.sprite.direction = 0

        if user_input[pygame.K_UP]:
            car.sprite.drive_state = True

        if user_input[pygame.K_RIGHT]:
            car.sprite.direction = 1

        if user_input[pygame.K_LEFT]:
            car.sprite.direction = -1

        # Draw the car and update its position
        car.draw(SCREEN)
        car.update()

        # Update the display
        pygame.display.update()

# Run the evaluation
eval_gen()

