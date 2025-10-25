from collections import namedtuple
import pygame
import random



Point = namedtuple('Point', 'x y')

BLUE = (0, 0, 255)
GREEN = (0, 255, 0)



BLOCK = 20 
width = 640
height = 480
class Game:
    def __init__(self):
        pygame.init()
        self.running = True
        self.display = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Simple Pygame Window")
        self.reset()

    def reset(self):
        self.direction = 'RIGHT'
        self.head = Point(width / 2, height / 2)
        self.score = 0
        self.frame_iteration = 0
        self.snake = [self.head,    
                      Point(self.head.x - BLOCK, self.head.y),
                      Point(self.head.x - (2 * BLOCK), self.head.y)]
        self.food = None
        self.place_food()

    def place_food(self):
        x = random.randint(0, (width - BLOCK) // BLOCK) * BLOCK
        y = random.randint(0, (height - BLOCK) // BLOCK) * BLOCK
        self.food = Point(x, y)
        if self.food in self.snake:
            self.place_food()

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        #check if hits boundary
        if pt.x > width - BLOCK or pt.x < 0 or pt.y > height - BLOCK or pt.y < 0:
            return True
        
        # check if snake eat itself
        if pt in self.snake[1:]:
            return True
        
        return False
    
    def ate_food(self):
        return self.head == self.food

    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.direction = 'LEFT'
                elif event.key == pygame.K_d:
                    self.direction = 'RIGHT'
                elif event.key == pygame.K_w:
                    self.direction = 'UP'
                elif event.key == pygame.K_s:
                    self.direction = 'DOWN'

        self.move(action)
        self.snake.insert(0, self.head)

        if self.is_collision():
            self.running = False
            return self.score
        
        if self.ate_food():
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()
        pygame.display.flip()
        self.clock.tick(10)
        self._update_ui()
        return self.score
    
    def _update_ui(self):
        self.display.fill(pygame.Color('black'))
        for pt in self.snake:
            pygame.draw.rect(self.display, pygame.Color('green'), pygame.Rect(pt.x, pt.y, BLOCK, BLOCK))

        pygame.draw.rect(self.display, pygame.Color('red'), pygame.Rect(self.food.x, self.food.y, BLOCK, BLOCK))
        text = pygame.font.Font(None, 36).render("Score: " + str(self.score), True, pygame.Color('white'))
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def run(self):
        while self.running:
            action = [1, 0, 0]
            score = self.play_step(action)
            print('Score:', score)
        pygame.quit()

    def move(self, action):
        clock_wise = ['RIGHT', 'DOWN', 'LEFT', 'UP']
        idx = clock_wise.index(self.direction)

        if action == [1, 0, 0]:
            new_dir = clock_wise[idx]  
        elif action == [0, 1, 0]:
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  
        else:  
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == 'RIGHT':
            x += BLOCK
        elif self.direction == 'LEFT':
            x -= BLOCK
        elif self.direction == 'DOWN':
            y += BLOCK
        elif self.direction == 'UP':
            y -= BLOCK

        self.head = Point(x, y)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.display.set_caption("Simple Pygame Window")
    pygame.quit()