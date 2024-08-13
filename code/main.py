from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        self.running = True
        self.reset_game()

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets()
        self.setup()

        # timers 
        self.bee_timer = Timer(100, func = self.create_bee, autostart = True, repeat = True)

    def reset_game(self):
        self.game_over = False
        self.lives = 20
        self.max_hp = 30
        self.current_hp = self.max_hp

    def create_bee(self):
        Bee(frames = self.bee_frames, 
            pos = ((self.level_width + WINDOW_WIDTH),(randint(0,self.level_height))), 
            groups = (self.all_sprites, self.enemy_sprites),
            speed = randint(300,500))

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')

        # sounds 
        self.audio = audio_importer('audio')

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet)
            if obj.name == 'Worm':
                Worm(self.worm_frames, pygame.Rect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        self.audio['music'].play(loops = -1)

    def collision(self):
        # bullets -> enemies 
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()
        
        # enemies -> player
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.current_hp -= 20
            if self.current_hp <= 0:
                self.lives -= 1
                self.current_hp = self.max_hp
                if self.lives <= 0:
                    self.game_over = True


    def game_over_screen(self):
        font = pygame.font.Font(None, 85)
        text = font.render('Game Over', True, (255, 80, 90))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(text, rect)
    
        font = pygame.font.Font(None, 36)
        restart_text = font.render('Press R to Restart', True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.display_surface.blit(restart_text, restart_rect)
        pygame.display.update()
        
        
        restarting = True
        while restarting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    restarting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Stop the music before restarting
                        self.audio['music'].stop()
                        self.reset_game()
                        self.setup()
                        restarting = False

    def draw_lives(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f'Lives: {self.lives}', True, (255, 255, 255))
        rect = text.get_rect(topleft=(10, 10))
        self.display_surface.blit(text, rect)

    def draw_hp(self):
        hp_bar_length = 200
        hp_bar_height = 20
        fill = (self.current_hp / self.max_hp) * hp_bar_length
        outline_rect = pygame.Rect(10, 40, hp_bar_length, hp_bar_height)
        fill_rect = pygame.Rect(10, 40, fill, hp_bar_height)
        pygame.draw.rect(self.display_surface, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), outline_rect, 2)

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
            if not self.game_over:
                # update
                self.bee_timer.update()
                self.all_sprites.update(dt)
                self.collision()

                # draw 
                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)
                self.draw_lives()
                self.draw_hp()
                pygame.display.update()
            else:
                self.game_over_screen()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
