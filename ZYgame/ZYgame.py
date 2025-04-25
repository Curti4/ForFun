import pygame
import random

hat_image= pygame.image.load("images/hat.jpg")
hat_size = (50, 50)
hat_image = pygame.transform.scale(hat_image, hat_size)
hat_rect = hat_image.get_rect()

hat=0
pygame.init()
game_state = "START"

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("幸運大轉盤")

npc_visible = True
npc_color = (0, 128, 255)
npc_size = 50
npc_x, npc_y = random.randint(0, width - npc_size), random.randint(height //2,height - npc_size)
npc_rect = pygame.Rect(npc_x, npc_y, npc_size, npc_size)

wheel_color = (200, 200 ,200)
wheel_center = (width // 2, height // 2)
whell_radius = 200
wheel_visible = False
wheel_rect= pygame.Rect(wheel_center[0] - whell_radius, wheel_center[1] - whell_radius, 2 * whell_radius, 2 * whell_radius)


button_color = (100,100, 100)
button_text = "Exit"
button_width, button_hight = 100,50
button_x = width - button_width - 20
button_y = 20
button_rect = pygame.Rect(button_x, button_y, button_width, button_hight)
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
button_surface = font.render(button_text, True, (0, 0, 0))
button_text_rect = button_surface.get_rect(center=button_rect.center)

hat_offsets = []
        
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if game_state == "START" and npc_rect.collidepoint(mouse_x, mouse_y):
                print("NPC clicked!")
                game_state = "WHEEL_VISIBLE"
            elif game_state == "WHEEL_VISIBLE" and wheel_rect.collidepoint(mouse_x, mouse_y):
                print("轉盤被點擊了！")
                random_number = random.randint(1, 1)
                if random_number == 1:
                    hat += 1
                    hat_offsets.append((random.randint(-10, 10), random.randint(-1, 1))) 
                else:
                    hat = 0
                    hat_offsets = []
                game_state = "RESULT"
            elif game_state == "RESULT" and button_rect.collidepoint(mouse_x, mouse_y):
                print("Exit button clicked!")
                game_state = "START"
                npc_x, npc_y = random.randint(0, width - npc_size), random.randint(height//2 ,height - npc_size)

    screen.fill((255, 255, 255))

    if game_state == "START":
        hat_text = font.render("hat: " + str(hat), True, (0, 0, 0))
        hat_text_rect = hat_text.get_rect(center=(width - 50, height - 20))

        screen.blit(hat_text, (width - 100, height- 100))
        npc_rect = pygame.Rect(npc_x, npc_y, npc_size, npc_size)
        pygame.draw.rect(screen, npc_color, npc_rect)
        for i in range(hat):
            hat_x_offset, hat_y_offset = hat_offsets[i]
            hat_rect.x = npc_x + (npc_size - hat_rect.width) // 2
            hat_rect.y = npc_y - i * hat_rect.height
            screen.blit(hat_image, (hat_rect.x + hat_x_offset, -50+hat_rect.y + hat_y_offset))

    elif game_state == "WHEEL_VISIBLE":
        pygame.draw.circle(screen, wheel_color, wheel_center, whell_radius)
    elif game_state == "RESULT":
        
        if random_number != 1:
            
            result_text = font.render("Not Golden Legend :<", True, (0, 0, 0))
            result_rect = result_text.get_rect(center=(width // 2, height // 4))
            screen.blit(result_text, result_rect)
            pygame.draw.rect(screen, button_color, button_rect)
            screen.blit(button_surface, button_text_rect)
        else:
            result_text = large_font.render("Golden Legend !", True, (0, 0, 0))
            result_rect = result_text.get_rect(center=(width // 2, height // 2))
            screen.blit(result_text, result_rect)
            pygame.draw.rect(screen, button_color, button_rect)
            screen.blit(button_surface, button_text_rect)

    pygame.display.flip()
pygame.quit()