import pygame
import random
import sys
import os
import math

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 初始化 Pygame 和基本設定 ---
pygame.init()
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("幸運大轉盤")
clock = pygame.time.Clock()

# --- 常量 ---
MAX_LEVEL = 4
HATS_PER_LEVEL = 3
ANIMATION_SPEED_MULTIPLIER = 3 # 動畫速度倍率

# --- 資源載入 ---
try:
    hat_level_images = []
    hat_level_size = (40, 40)
    # 調整備用顏色以匹配新要求
    fallback_colors = [(173, 216, 230), (255, 182, 193), (150, 150, 150), (200, 150, 150)] # 藍, 粉, 灰, 備用
    for i in range(1, MAX_LEVEL + 1):
        try:
            img_path = resource_path(f"images/hat{i}.jpg")
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, hat_level_size)
            hat_level_images.append(img)
            print(f"成功載入: images/hat{i}.jpg")
        except pygame.error as e:
            print(f"無法載入圖片: images/hat{i}.jpg - {e}")
            img = pygame.Surface(hat_level_size, pygame.SRCALPHA)
            # 使用索引 i-1，並處理可能的索引超出
            color_index = min(i - 1, len(fallback_colors) - 1)
            img.fill(fallback_colors[color_index] + (255,))
            pygame.draw.rect(img, (0,0,0, 255), img.get_rect(), 1)
            hat_level_images.append(img)

    # NPC 頭上帽子圖片 (初始為 Level 1)
    npc_hat_size = (50, 50)
    npc_hat_images_scaled = [pygame.transform.scale(img, npc_hat_size) for img in hat_level_images] # 預先縮放好
    npc_hat_image = npc_hat_images_scaled[0] # 初始用 Level 1
    npc_hat_rect = npc_hat_image.get_rect()

except Exception as e:
    print(f"資源載入時發生錯誤: {e}")
    pygame.quit()
    sys.exit()

# --- 字體設定 ---
try:
    print("使用系統預設字體 (可能不支援中文)")
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 24)
except Exception as e:
    print(f"載入字體失敗: {e}. 使用 Pygame 預設字體。")
    # Fallback fonts
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 24)

# --- 顏色定義 ---
COLOR_LIGHT_BLUE = (173, 216, 230) # 淡藍色 (取代黃色)
COLOR_LIGHT_RED = (255, 182, 193) # 淡紅色/粉色 (取代紅色)
COLOR_GRAY = (150, 150, 150)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_NPC = (0, 128, 255)
COLOR_BUTTON = (100, 100, 100)
COLOR_BUTTON_HOVER = (150, 150, 150)
COLOR_TEXT_DARK = (50, 50, 50)
COLOR_WIN = (0, 128, 0) # 結果文字顏色保持不變
COLOR_LOSE = (255, 0, 0) # 結果文字顏色保持不變
COLOR_NOTHING = (100, 100, 100) # 結果文字顏色保持不變

# --- 帽子等級和里程碑 ---
# 結構: (Level ID, Required Count for NEXT level, Image for this level)
# 注意：這裡的 Required Count 實際上是達到這個 Level 需要的累積數量，但我們的邏輯是每級10個
# 重新定義 milestones 結構，使其更符合升級邏輯
# (Target Level to reach, Required Count in previous level, Image representing the target level)
hat_milestones_data = []
if len(hat_level_images) >= MAX_LEVEL: # 確保圖片足夠
     hat_milestones_data = [
        (1, HATS_PER_LEVEL, hat_level_images[0]), # 升到 Level 1 (初始)
        (2, HATS_PER_LEVEL, hat_level_images[1]), # 升到 Level 2 需要 Level 1 滿 10 個
        (3, HATS_PER_LEVEL, hat_level_images[2]), # 升到 Level 3 需要 Level 2 滿 10 個
        (4, HATS_PER_LEVEL, hat_level_images[3]), # 升到 Level 4 需要 Level 3 滿 10 個
    ]
else:
    print("錯誤：載入的帽子圖片數量不足！")
    # 可以添加退出或其他處理


# --- 遊戲狀態變數 ---
game_state = "START"
player_level = 1 # 玩家當前等級 (1-4)
hat = 0          # 當前等級收集到的帽子數量
hat_offsets = [] # NPC 頭上帽子的隨機偏移 (每個 Level 重置)

# --- NPC 設定 ---
npc_visible = True
npc_size = 50
npc_x, npc_y = random.randint(0, width - npc_size), random.randint(height // 2 + 50, height - npc_size - 20)
npc_rect = pygame.Rect(npc_x, npc_y, npc_size, npc_size)

# --- 轉盤設定 ---
wheel_center = (width // 2, height // 2)
wheel_radius = 200
wheel_rect = pygame.Rect(wheel_center[0] - wheel_radius, wheel_center[1] - wheel_radius, 2 * wheel_radius, 2 * wheel_radius)

# --- 轉盤動畫狀態變數 (速度加快) ---
current_angle = 0.0
target_angle = -1.0
is_spinning = False
is_decelerating = False
current_rotation_speed = math.radians(360 * ANIMATION_SPEED_MULTIPLIER) # 加快轉速
spin_start_time = 0
spin_duration = max(500, 2000 // ANIMATION_SPEED_MULTIPLIER) # 縮短旋轉時間 (加下限)
stop_duration = max(800, 3000 // ANIMATION_SPEED_MULTIPLIER) # 縮短停止時間 (加下限)
angle_before_stopping = 0.0
total_angle_to_spin_decel = 0.0

# --- 轉盤結果變數 ---
result_type = ""
nhat_earned = 0

# --- 按鈕設定 ---
button_width, button_height = 100, 50
button_x = width - button_width - 20
button_y = 20
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
button_surface = font.render("Back", True, COLOR_BLACK)
button_text_rect = button_surface.get_rect(center=button_rect.center)

# --- 預先繪製轉盤表面 (更新顏色) ---
wheel_surface = pygame.Surface((wheel_radius * 2, wheel_radius * 2), pygame.SRCALPHA)
center_x_surf, center_y_surf = wheel_radius, wheel_radius
angle_step = math.radians(1)

# 區域角度保持不變，但繪製顏色更新
angle_win_start = 0.0           # Win 區域 (原黃色)
angle_win_end = math.pi
angle_lose_start = math.pi      # Lose 區域 (原紅色)
angle_lose_end = angle_lose_start + (math.pi * 2 * 0.1)
angle_nothing_start = angle_lose_end # Nothing 區域 (灰色)
angle_nothing_end = 2 * math.pi

def create_sector_points_pygame_while(start_angle, end_angle):
    # (函數內容不變)
    points = [(center_x_surf, center_y_surf)]
    angle = start_angle
    num_steps = max(1, int(abs(end_angle - start_angle) / angle_step))
    actual_step = (end_angle - start_angle) / num_steps
    for i in range(num_steps + 1):
        angle = start_angle + i * actual_step
        x = center_x_surf + wheel_radius * math.cos(angle)
        y = center_y_surf - wheel_radius * math.sin(angle)
        points.append((x, y))
    return points

# 繪製各個區域 (使用新顏色)
points_win = create_sector_points_pygame_while(angle_win_start, angle_win_end)
pygame.draw.polygon(wheel_surface, COLOR_LIGHT_BLUE + (180,), points_win) # 淡藍色

points_lose = create_sector_points_pygame_while(angle_lose_start, angle_lose_end)
pygame.draw.polygon(wheel_surface, COLOR_LIGHT_RED + (180,), points_lose) # 淡紅色

points_nothing = create_sector_points_pygame_while(angle_nothing_start, angle_nothing_end)
pygame.draw.polygon(wheel_surface, COLOR_GRAY + (180,), points_nothing) # 灰色


# --- 輔助函數：結算結果並改變狀態 ---
def finalize_spin_result():
    global hat, hat_offsets, game_state, is_spinning, is_decelerating, target_angle, current_angle
    print("結算結果...")
    current_angle = target_angle # 強制設定最終角度

    # --- 結算帽子 (只影響當前等級數量) ---
    if result_type == "win":
        hat += nhat_earned
        # 為新增的帽子添加偏移量 (使用當前等級的偏移)
        for _ in range(nhat_earned):
            if len(hat_offsets) < 50: # 限制顯示上限
                 # 確保偏移列表長度不超過實際帽子數
                if len(hat_offsets) < hat:
                    hat_offsets.append((random.randint(-5, 5), random.randint(-2, 2)))
            else:
                break
        print(f"獲得 {nhat_earned} 個 Level {player_level} 帽子, 現在有 {hat} 個")
    elif result_type == "lose":
        print(f"失去所有 Level {player_level} 帽子!")
        hat = 0
        hat_offsets = [] # 清空當前等級的帽子

    game_state = "RESULT"
    is_spinning = False
    is_decelerating = False
    target_angle = -2.0 # 標記完成


# --- 主遊戲迴圈 ---
running = True
while running:
    current_time = pygame.time.get_ticks()
    dt = clock.tick(60) / 1000.0 # 限制FPS在60
    mouse_pos = pygame.mouse.get_pos()

    # --- 事件處理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mouse_x, mouse_y = event.pos
                if game_state == "START":
                    # 1. 點擊 NPC 開始轉盤
                    if npc_rect.collidepoint(mouse_x, mouse_y) and not is_spinning and not is_decelerating and player_level < MAX_LEVEL: # 最高級不能再轉? (或者可以?) 這裡先設為不到最高級才能轉
                        print("NPC clicked!")
                        game_state = "WHEEL_VISIBLE"
                        is_spinning = True
                        is_decelerating = False
                        target_angle = -1.0
                        spin_start_time = current_time
                        result_type = ""
                        nhat_earned = 0
                    elif npc_rect.collidepoint(mouse_x, mouse_y) and player_level >= MAX_LEVEL:
                         print("已達到最高等級!")

                    # 2. 點擊里程碑升級
                    elif player_level < MAX_LEVEL: # 只有未滿級才能升級
                        required_hats = HATS_PER_LEVEL # 每級都需要10個
                        can_upgrade = hat >= required_hats

                        # 計算第一個可見里程碑的點擊區域
                        # (需要知道哪個是第一個可見的)
                        milestone_display_index = player_level -1 # 當前等級對應的 data 索引
                        if milestone_display_index < len(hat_milestones_data):
                            target_level, req_count, img = hat_milestones_data[milestone_display_index]
                            # 顯示的是下一個目標，所以實際圖片是 player_level 的圖
                            # 修正: 我們應該檢查點擊的是 "升到下一級" 的按鈕
                            # 顯示的前三個里程碑是從 player_level 開始
                            # 所以第一個顯示的是 level player_level 的目標
                            milestone_x_start = 20
                            milestone_spacing = 110
                            milestone_y = 15
                            first_milestone_img = hat_milestones_data[player_level-1][2] # 當前等級的圖片
                            # 不對，應該是下個等級的圖片和要求
                            # 顯示的應該是 player_level, player_level+1, player_level+2 的里程碑（如果存在）
                            # 我們需要點擊的是 *當前* 等級收集滿後，觸發升級的那個顯示項目
                            # 這個項目代表的是 "收集滿 level player_level 的帽子"
                            if player_level -1 < len(hat_milestones_data):
                                current_milestone_img = hat_milestones_data[player_level-1][2]
                                first_milestone_rect = current_milestone_img.get_rect(topleft=(milestone_x_start, milestone_y))

                                if first_milestone_rect.collidepoint(mouse_x, mouse_y):
                                    if can_upgrade:
                                        print(f"升級! 從 Level {player_level} 到 Level {player_level + 1}")
                                        player_level += 1
                                        hat = 0 # 重置當前等級帽子數量
                                        hat_offsets = [] # 清空視覺堆疊
                                        # 更新NPC頭上的帽子圖片
                                        if player_level - 1 < len(npc_hat_images_scaled):
                                            npc_hat_image = npc_hat_images_scaled[player_level - 1]
                                        else:
                                             print(f"警告: 找不到 Level {player_level} 的 NPC 帽子圖片")
                                    else:
                                        print(f"還需要 {required_hats - hat} 個 Level {player_level} 帽子才能升級")


                elif game_state == "WHEEL_VISIBLE":
                    # CLICK TO SKIP (只在結果決定後有效)
                    if target_angle >= 0:
                        finalize_spin_result()

                elif game_state == "RESULT":
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        print("Back button clicked!")
                        game_state = "START"
                        npc_x, npc_y = random.randint(0, width - npc_size), random.randint(height // 2 + 50, height - npc_size - 20)
                        npc_rect.topleft = (npc_x, npc_y)


    # --- 遊戲狀態邏輯與繪圖 ---
    screen.fill(COLOR_WHITE)

    if game_state == "START":
        # --- 繪製頂部帽子進度 (根據當前等級顯示接下來的目標) ---
        milestone_x_start = 20
        milestone_y = 15
        milestone_spacing = 110
        displayed_count = 0
        for i in range(player_level - 1, len(hat_milestones_data)):
            if displayed_count >= 3: # 最多顯示3個
                break
            target_level, req_count, img = hat_milestones_data[i]
            # 計算顯示位置
            display_x = milestone_x_start + displayed_count * milestone_spacing
            img_rect = img.get_rect(topleft=(display_x, milestone_y))
            screen.blit(img, img_rect)
            # 顯示需要的數量 (總是 10)
            text_surf = small_font.render(f"x{HATS_PER_LEVEL}", True, COLOR_TEXT_DARK)
            text_rect = text_surf.get_rect(midleft=(img_rect.right + 5, img_rect.centery))
            screen.blit(text_surf, text_rect)

            # 如果是第一個顯示的里程碑（即當前努力的目標），並且可以升級，給個提示？(可選)
            if displayed_count == 0 and player_level < MAX_LEVEL and hat >= HATS_PER_LEVEL:
                 # 畫一個綠色邊框提示可以點擊升級
                 pygame.draw.rect(screen, COLOR_WIN, img_rect, 2)

            displayed_count += 1
        # 如果已達最高級，顯示提示
        if player_level >= MAX_LEVEL:
             max_level_text = font.render("Max Level!", True, COLOR_WIN)
             max_level_rect = max_level_text.get_rect(topleft=(milestone_x_start, milestone_y + hat_level_size[1] + 10))
             screen.blit(max_level_text, max_level_rect)


        # --- 繪製右上角當前帽子數量 (顯示當前等級的帽子和數量) ---
        current_hat_display_img = hat_level_images[player_level - 1] # 使用當前等級的圖片
        current_hat_img_rect = current_hat_display_img.get_rect(topright=(width - 60, 15))
        screen.blit(current_hat_display_img, current_hat_img_rect)

        # 顯示當前等級收集的數量
        hat_count_text = font.render(f": {hat}/{HATS_PER_LEVEL if player_level < MAX_LEVEL else '--'}", True, COLOR_BLACK)
        hat_count_rect = hat_count_text.get_rect(midleft=(current_hat_img_rect.right + 5, current_hat_img_rect.centery))
        screen.blit(hat_count_text, hat_count_rect)


        # --- 繪製 NPC ---
        npc_rect.topleft = (npc_x, npc_y)
        pygame.draw.rect(screen, COLOR_NPC, npc_rect)

        # --- 繪製疊加在 NPC 頭上的帽子 (使用當前等級的帽子圖片) ---
        # 確保 npc_hat_image 是當前等級的
        if player_level - 1 < len(npc_hat_images_scaled):
            current_npc_hat_img = npc_hat_images_scaled[player_level - 1]
            current_npc_hat_rect = current_npc_hat_img.get_rect() # 獲取正確尺寸
            # 使用 hat_offsets 繪製視覺堆疊 (最多 hat 個)
            for i in range(len(hat_offsets)):
                 if i >= hat: # 確保不畫超過擁有的數量
                      # 理論上 finalize_spin_result 裡應該會同步，但加個保險
                      hat_offsets = hat_offsets[:hat]
                      break
                 hat_x_offset, hat_y_offset = hat_offsets[i]
                 hat_draw_x = npc_x + (npc_size - current_npc_hat_rect.width) // 2 + hat_x_offset
                 hat_draw_y = npc_y - (i * (current_npc_hat_rect.height * 0.75)) + hat_y_offset
                 screen.blit(current_npc_hat_img, (hat_draw_x, hat_draw_y - current_npc_hat_rect.height))
        else:
             print(f"錯誤: 無法確定 Level {player_level} 的 NPC 帽子圖片")


    elif game_state == "WHEEL_VISIBLE":
        # --- 更新轉盤角度 ---
        if is_spinning:
            elapsed_time = current_time - spin_start_time
            if target_angle < 0: # 尚未決定結果
                current_angle += current_rotation_speed * dt
                current_angle %= (2 * math.pi)
                if elapsed_time >= spin_duration:
                    # --- 決定結果 ---
                    print("決定結果...")
                    wheel_probab = random.randint(1, 100)
                    nhat_earned_temp = 0
                    target_random_range = math.pi * 0.1

                    if wheel_probab <= 50: # Win - Light Blue
                        result_type = "win"
                        nhat_earned_temp = random.randint(1, 3)
                        target_angle = math.pi / 2.0 + random.uniform(-target_random_range, target_random_range)
                    elif wheel_probab <= 60: # Lose - Light Red
                        result_type = "lose"
                        nhat_earned_temp = 0
                        target_angle = 1.1 * math.pi + random.uniform(-target_random_range / 2, target_random_range / 2)
                    else: # Nothing - Gray
                        result_type = "nothing"
                        nhat_earned_temp = 0
                        target_angle = 1.6 * math.pi + random.uniform(-target_random_range, target_random_range)

                    target_angle %= (2 * math.pi)
                    nhat_earned = nhat_earned_temp # 儲存本次轉到的數量

                    # --- 開始減速 ---
                    print(f"結果: {result_type}, 獲得: {nhat_earned}, 目標角度: {math.degrees(target_angle):.1f}")
                    is_decelerating = True
                    angle_before_stopping = current_angle
                    angle_diff = (target_angle - current_angle + 2 * math.pi) % (2 * math.pi)
                    extra_rotations = 2 * math.pi * random.randint(1, 2) # 隨機多轉幾圈
                    total_angle_to_spin_decel = angle_diff + extra_rotations
                    spin_start_time = current_time # 重置減速計時器

            elif is_decelerating: # 正在減速
                elapsed_stop_time = current_time - spin_start_time
                if elapsed_stop_time < stop_duration:
                    fraction = elapsed_stop_time / stop_duration
                    ease_fraction = 1.0 - (1.0 - fraction)**3 # Cubic ease-out
                    current_angle = (angle_before_stopping + total_angle_to_spin_decel * ease_fraction) % (2 * math.pi)
                else:
                    finalize_spin_result() # 自然停止

        # --- 繪製轉盤 ---
        rotated_wheel = pygame.transform.rotate(wheel_surface, math.degrees(-current_angle))
        rotated_rect = rotated_wheel.get_rect(center=wheel_center)
        screen.blit(rotated_wheel, rotated_rect)

        # --- 繪製指針 ---
        pointer_color = COLOR_BLACK
        pointer_tip_offset = 10
        pointer_base_offset = -5
        pointer_half_width = 8
        tip_x = wheel_center[0] + wheel_radius + pointer_tip_offset
        tip_y = wheel_center[1]
        base_x = wheel_center[0] + wheel_radius + pointer_base_offset
        base_y1 = wheel_center[1] - pointer_half_width
        base_y2 = wheel_center[1] + pointer_half_width
        pygame.draw.polygon(screen, pointer_color, [(tip_x, tip_y), (base_x, base_y1), (base_x, base_y2)])

        # --- 繪製轉盤中心點 ---
        pygame.draw.circle(screen, COLOR_TEXT_DARK, wheel_center, 10)

        # --- 繪製圖例 (更新顏色) ---
        legend_items = [
            (COLOR_LIGHT_BLUE, f"Win (1-3 Level {player_level} Hats)"), # 顯示當前等級
            (COLOR_LIGHT_RED, "Lose (All Current Hats)"),
            (COLOR_GRAY, "Nothing")
        ]
        legend_x = width - 220 # 稍微左移以容納更長文字
        legend_y = height - 80 # 稍微上移
        box_size = 15
        line_height = 25

        for i, (color, text) in enumerate(legend_items):
            current_y = legend_y + i * line_height
            pygame.draw.rect(screen, color, (legend_x, current_y, box_size, box_size))
            pygame.draw.rect(screen, COLOR_BLACK, (legend_x, current_y, box_size, box_size), 1)
            text_surf = small_font.render(text, True, COLOR_BLACK)
            text_rect = text_surf.get_rect(midleft=(legend_x + box_size + 8, current_y + box_size // 2))
            screen.blit(text_surf, text_rect)


    elif game_state == "RESULT":
        # --- 顯示結果文字 ---
        result_text_surface = None
        text_color = COLOR_BLACK
        display_text = ""

        if result_type == "win":
            display_text = f"You got {nhat_earned}!" # 只顯示數量
            text_color = COLOR_WIN
            result_text_surface = large_font.render(display_text, True, text_color)
        elif result_type == "lose":
            display_text = "Hahahaha"
            text_color = COLOR_LOSE
            result_text_surface = large_font.render(display_text, True, text_color)
        else: # nothing
            display_text = "Sad :<"
            text_color = COLOR_NOTHING
            result_text_surface = font.render(display_text, True, text_color)

        if result_text_surface:
            result_rect = result_text_surface.get_rect(center=(width // 2, height // 2 - 20)) # 文字稍微上移
            screen.blit(result_text_surface, result_rect)
            # 顯示獲得/失去的帽子等級
            level_info_text = ""
            if result_type == "win":
                 level_info_text = f"(Level {player_level} Hats)"
            elif result_type == "lose":
                 level_info_text = f"(Lost Level {player_level} Hats)"
            if level_info_text:
                 level_info_surf = small_font.render(level_info_text, True, text_color) # 用同樣顏色
                 level_info_rect = level_info_surf.get_rect(center=(width // 2, height // 2 + 20)) # 在主文字下方
                 screen.blit(level_info_surf, level_info_rect)


        # --- 繪製返回按鈕 ---
        button_current_color = COLOR_BUTTON
        if button_rect.collidepoint(mouse_pos):
             button_current_color = COLOR_BUTTON_HOVER
        pygame.draw.rect(screen, button_current_color, button_rect, border_radius=5)
        screen.blit(button_surface, button_text_rect)


    # --- 更新顯示 ---
    pygame.display.flip()

# --- 退出 Pygame ---
pygame.quit()
sys.exit()