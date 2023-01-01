# Please don't roast me, I coded this at 1 am :)
import math
import random
import pygame

WIDTH, HEIGHT = 1000, 800
FPS = 60
g = 9.81 / 2 / FPS

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fireworks")


class Particle:
    max_v = 4
    r = 2
    def __init__(self, coordinates, velocities, color, friction=None, opacity=1, decay=.004):
        self.x, self.y = coordinates
        self.vx, self.vy = velocities
        self.friction = friction or 0.999 - random.random() * 0.005
        self.lifetime_frames = 30 * random.random() + 40
        self.lifetime = 0
        self.color = color
        self.opacity = opacity
        self.opacity_decay = (decay - .001) * random.random() + .001

    def update(self):
        self.vx *= self.friction
        self.vy *= self.friction
        self.x += self.vx
        self.y += self.vy
        self.color = tuple(map(lambda v: int(v * self.opacity), self.color))
        self.opacity -= self.opacity_decay
        self.lifetime += 1

    def is_off(self):
        return self.lifetime >= self.lifetime_frames or self.opacity <= .9

    def draw(self):
        pygame.draw.circle(WIN, self.color, (int(self.x), int(self.y)), self.r)
    
class Line(Particle):
    def __init__(self, start, end, velocities, color, opacity=1, decay=.004):
        super().__init__(end, velocities, color, decay=decay)
        self.start_x, self.start_y = start
        self.start_vx, self.start_vy = velocities
        self.start_friction = self.friction * 0.9
    
    def update(self):
        super().update()
        self.start_vx *= self.start_friction
        self.start_vy *= self.start_friction
        self.start_x += self.start_vx
        self.start_y += self.start_vy

    def draw(self):
        pygame.draw.line(WIN, self.color, (int(self.start_x), int(self.start_y)), (int(self.x), int(self.y)), self.r)


class Firework:
    colors = [(r,g,b) for r in range(50, 255, 5) for b in range(50, 255, 5) for g in range(50, 255, 5)]
    explosion_height_range = (100, 350)
    r = 4

    def __init__(self, x=None, rainbow=False, color_range=1000, num_particles=100, delay_frames=0):
        self.x = x or random.randint(0, WIDTH)
        self.y = HEIGHT
        self.vx, self.vy = 0, random.randint(-15, -10)
        self.particles = []
        self.num_particles = num_particles
        self.explosion_height = random.randint(*self.explosion_height_range)
        self.exploded = False
        self.finished = False
        self.delay_frames = delay_frames
        self.frames = 0

        color_range = min(len(self.colors), color_range)
        if rainbow:
            self.start_index = 0
            self.end_index = len(self.colors) - 1
        else:
            self.start_index = random.randint(0, len(self.colors) - (color_range + 1))
            self.end_index = self.start_index + color_range

        self.color_range = self.end_index - self.start_index
        self.color = self.colors[random.randint(self.start_index, self.end_index)]

    def update(self):
        if self.delay_frames:
            if self.frames <= self.delay_frames: 
                self.frames += 1
                return
            self.delay_frames = None
        if not self.exploded:
            self.vy += g
            self.y += self.vy
            self.draw()
            self.exploded = self.y <= self.explosion_height or self.vy >= 0
            if self.exploded:
                self.explode()
            return

        for particle in self.particles:
            particle.update()
            particle.draw()

        self.particles = list(filter(lambda p: not p.is_off(), self.particles))
        self.finished = not self.particles

    def draw(self):
        pygame.draw.circle(WIN, self.color, (int(self.x), int(self.y)), self.r)

    def explode(self):
        self.exploded = True
        num_lines = int(self.num_particles * .2)
        num_circles = int(self.num_particles * .8)
        num_circles += self.num_particles - (num_circles + num_lines)
        for i in range(1, num_circles + 1):
            color_index = int(self.start_index + self.color_range * (i / num_circles))
            pvx = math.cos(math.pi * num_circles / i) * ((Particle.max_v - .5) * random.random() + .5)
            pvy = math.sin(math.pi * num_circles / i) * ((Particle.max_v - .5) * random.random() + .5)
            self.particles.append(Particle((self.x, self.y), (pvx, pvy), self.colors[color_index]))
        
        for i in range(1, num_lines + 1):
            color_index = int(self.start_index + self.color_range * (i / num_lines))
            pvx = math.cos(math.pi * num_lines / i) * ((Particle.max_v - .5) * random.random() + .5)
            pvy = math.sin(math.pi * num_lines / i) * ((Particle.max_v - .5) * random.random() + .5)
            self.particles.append(Line((self.x, self.y), (self.x, self.y), (pvx, pvy), self.colors[color_index]))

def manage_fireworks(fireworks: list[Firework]):
    WIN.fill((0, 0, 0))
    initial_n = len(fireworks)
    for firework in fireworks:
        firework.update()
    fireworks = list(filter(lambda f: not f.finished, fireworks))
    for _ in range(initial_n - len(fireworks)):
        rainbow = random.randint(0, 1)
        fireworks.append(Firework(rainbow=rainbow))
    pygame.display.update()
    return fireworks

def init_fireworks(num_fireworks: int):
    fireworks = []
    for _ in range(num_fireworks):
        fireworks.append(Firework(delay_frames=random.randint(0, 120)))
    return fireworks

if __name__ == '__main__':
    clock = pygame.time.Clock()
    running = True
    fireworks = init_fireworks(15)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        fireworks = manage_fireworks(fireworks)
        clock.tick(FPS)
