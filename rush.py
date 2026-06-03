import pygame
import random
import math
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Red Rush: Drift Escape")
BG_COLOR = (25, 40, 25)       
GRID_COLOR = (40, 60, 40)     
PLAYER_COLOR = (230, 30, 30)
POLICE_COLOR = (30, 80, 230)
TEXT_COLOR = (255, 255, 255)
clock = pygame.time.Clock()
FPS = 60
class SmokeParticle:
    def __init__(self, x, y, is_drifting):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        if is_drifting:
            self.radius = random.uniform(6, 12)
            gray_shade = random.randint(100, 140)
        else:
            self.radius = random.uniform(3, 6)
            gray_shade = random.randint(200, 230)   
        self.color = [gray_shade, gray_shade, gray_shade]
        self.alpha = 180  
        self.lifetime = random.randint(20, 40) 
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius += 0.25      
        self.alpha -= 5          
        self.lifetime -= 1
    def draw(self, surface, cam_x, cam_y):
        if self.alpha > 0:
            screen_x = int(self.x - cam_x + SCREEN_WIDTH // 2)
            screen_y = int(self.y - cam_y + SCREEN_HEIGHT // 2)
            particle_surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (self.color[0], self.color[1], self.color[2], self.alpha), 
                               (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(particle_surf, (screen_x - int(self.radius), screen_y - int(self.radius)))
class PlayerCar:
    def __init__(self):
        self.x = 0  
        self.y = 0
        self.width = 20
        self.height = 40
        self.angle = 0        
        self.speed = 8        
        self.max_speed = 10
        self.acceleration = 0.4
        self.drag = 0.1
        self.steering_speed = 6
        self.vx = 2             
        self.vy = 2             
        self.drift_factor = 0.88 
        self.is_drifting = False
        self.health = 100
    def update(self):
        # Default states
        steer_left = False
        steer_right = False
        accelerating = False
        braking = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: steer_left = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: steer_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]: accelerating = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: braking = True

        # 2. INVISIBLE MOBILE SCREEN TOUCH LOGIC
        mouse_pressed = pygame.mouse.get_pressed()[0] 
        if mouse_pressed:
            mx, my = pygame.mouse.get_pos() # Get the exact X coordinate of touch
            
            # Left 40% of screen width
            if mx < SCREEN_WIDTH * 0.40:
                steer_left = True
                accelerating = True
                
            # Right 40% of screen width
            elif mx > SCREEN_WIDTH * 0.60:
                steer_right = True
                accelerating = True
                
            # Center 20% of screen width (Between 40% and 60%)
            else:
                accelerating = True
                # Stays straight because steer_left and steer_right remain False!

        # Apply steering math
        if steer_left:
            self.angle += self.steering_speed * (self.speed / self.max_speed if self.speed > 0 else 1)
        if steer_right:
            self.angle -= self.steering_speed * (self.speed / self.max_speed if self.speed > 0 else 1)

        # Apply speed math
        if accelerating:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif braking:
            self.speed = max(self.speed - self.acceleration * 1.5, -self.max_speed / 2)
        else:
            if self.speed > 0: self.speed -= self.drag
            elif self.speed < 0: self.speed += self.drag
            if abs(self.speed) < 0.1: self.speed = 0
        forward_x = math.sin(math.radians(self.angle)) * self.speed
        forward_y = math.cos(math.radians(self.angle)) * self.speed

        self.vx = self.vx * self.drift_factor + forward_x * (1 - self.drift_factor)
        self.vy = self.vy * self.drift_factor + forward_y * (1 - self.drift_factor)

        move_angle = math.degrees(math.atan2(self.vx, self.vy))
        angle_diff = abs((self.angle % 360) - (move_angle % 360))
        self.is_drifting = self.speed > 3 and (15 < angle_diff < 345)

        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        screen_x = SCREEN_WIDTH // 2
        screen_y = SCREEN_HEIGHT // 2

        car_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, PLAYER_COLOR, (0, 0, self.width, self.height), border_radius=4)
        pygame.draw.rect(car_surf, (200, 230, 255), (2, 5, self.width - 4, 8))
        
        rotated_surf = pygame.transform.rotate(car_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(screen_x, screen_y))
        surface.blit(rotated_surf, new_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)


class PoliceCar:
    def __init__(self, player_x, player_y):
        angle = random.uniform(0, 2 * math.pi)
        spawn_dist = 500  
        self.x = player_x + math.sin(angle) * spawn_dist
        self.y = player_y + math.cos(angle) * spawn_dist
        
        self.width = 20
        self.height = 40
        self.speed = random.uniform(3.0, 4.0)
        self.angle = 0
        self.active = True

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            self.angle = math.degrees(math.atan2(dx, dy))

    def draw(self, surface, cam_x, cam_y):
        screen_x = int(self.x - cam_x + SCREEN_WIDTH // 2)
        screen_y = int(self.y - cam_y + SCREEN_HEIGHT // 2)

        if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
            cop_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(cop_surf, POLICE_COLOR, (0, 0, self.width, self.height), border_radius=4)
            light_color = (255, 0, 0) if pygame.time.get_ticks() % 200 < 100 else (0, 0, 255)
            pygame.draw.rect(cop_surf, light_color, (2, 15, self.width - 4, 6))

            rotated_surf = pygame.transform.rotate(cop_surf, self.angle)
            new_rect = rotated_surf.get_rect(center=(screen_x, screen_y))
            surface.blit(rotated_surf, new_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)


def draw_open_world(surface, cam_x, cam_y):
    surface.fill(BG_COLOR)
    grid_size = 100
    
    start_x = int(cam_x - SCREEN_WIDTH // 2) // grid_size * grid_size
    end_x = start_x + SCREEN_WIDTH + grid_size * 2
    start_y = int(cam_y - SCREEN_HEIGHT // 2) // grid_size * grid_size
    end_y = start_y + SCREEN_HEIGHT + grid_size * 2

    for x in range(start_x, end_x, grid_size):
        screen_x = x - cam_x + SCREEN_WIDTH // 2
        pygame.draw.line(surface, GRID_COLOR, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)

    for y in range(start_y, end_y, grid_size):
        screen_y = y - cam_y + SCREEN_HEIGHT // 2
        pygame.draw.line(surface, GRID_COLOR, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)


# --- MAIN ENGINE LOOP ---
def main():
    player = PlayerCar()
    police_squad = []
    smoke_particles = [] 
    score = 0
    drift_points = 0
    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 36, bold=True)

    SPAWN_COP_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_COP_EVENT, 2500) 

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_COP_EVENT and not game_over:
                if len(police_squad) < 8:
                    police_squad.append(PoliceCar(player.x, player.y))
            
            if game_over and (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN):
                main()
                return

        if not game_over:
            player.update()

            # Generate particle smoke trails
            if abs(player.speed) > 1:
                smoke_particles.append(SmokeParticle(player.x, player.y, is_drifting=False))
                if player.is_drifting:
                    for _ in range(3): 
                        smoke_particles.append(SmokeParticle(player.x, player.y, is_drifting=True))

            camera_x = player.x
            camera_y = player.y

            for particle in smoke_particles:
                particle.update()
            smoke_particles = [p for p in smoke_particles if p.lifetime > 0]

            # AI Chase Updates
            player_rect = player.get_rect()
            for cop in police_squad:
                cop.update(player.x, player.y)
                if cop.get_rect().colliderect(player_rect):
                    player.health -= 0.5
                    if player.health <= 0:
                        game_over = True

            # Inter-Cop Crashes
            for i in range(len(police_squad)):
                for j in range(i + 1, len(police_squad)):
                    if police_squad[i].active and police_squad[j].active:
                        if police_squad[i].get_rect().colliderect(police_squad[j].get_rect()):
                            police_squad[i].active = False
                            police_squad[j].active = False
                            score += 150

            police_squad = [cop for cop in police_squad if cop.active]

            if player.is_drifting:
                drift_points += int(abs(player.speed) * 0.5)
                score += 1
            else:
                if drift_points > 0:
                    score += drift_points 
                    drift_points = 0
        draw_open_world(screen, camera_x, camera_y)

        for particle in smoke_particles:
            particle.draw(screen, camera_x, camera_y)

        for cop in police_squad:
            cop.draw(screen, camera_x, camera_y)
        player.draw(screen)
        score_txt = font.render(f"Score: {score}", True, TEXT_COLOR)
        health_txt = font.render(f"Health: {max(0, int(player.health))}%", True, TEXT_COLOR)
        screen.blit(score_txt, (20, 20))
        screen.blit(health_txt, (20, 50))

        if player.is_drifting and not game_over:
            drift_txt = big_font.render(f"DRIFT: +{drift_points}", True, (255, 200, 0))
            screen.blit(drift_txt, (SCREEN_WIDTH // 2 - drift_txt.get_width() // 2, 80))

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            go_txt = big_font.render("WRECKED!", True, (255, 50, 50))
            restart_txt = font.render("Press SPACEBAR or TAP SCREEN to Restart", True, TEXT_COLOR)
            screen.blit(go_txt, (SCREEN_WIDTH // 2 - go_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_txt, (SCREEN_WIDTH // 2 - restart_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
if __name__ == "__main__":
    main()