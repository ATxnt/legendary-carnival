#ailen_invasion.py-主循环
import pygame
from pygame.sprite import Group
from settings import Settings
from ship import Ship
import game_functions as gf
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button


def run_game():
	# 初始化游戏并创建一个屏幕对象
	pygame.init()
	screen = Settings()
	ai_settings =Settings()
	screen = pygame.display.set_mode(
		(screen.screen_width, screen.screen_height))
	pygame.display.set_caption("Alien Invasion")


	# 创建一个play按钮
	play_button = Button(ai_settings, screen, "play")


	# 创建一艘飞船
	ship = Ship(ai_settings, screen)
	#创建一个用于储存子弹与外星人的编组
	bullets = Group()
	aliens = Group()
	#创建一艘外星人
	gf.create_fleet(ai_settings, screen, ship, aliens)

	#创建一个用于存储游戏统计信息的实例,并创建记分牌
	stats = GameStats(ai_settings)
	sb = Scoreboard(ai_settings, screen, stats)

	# 开始游戏的主循环
	while True:
		gf.check_events(ai_settings, screen, stats, play_button, ship, \
														aliens, bullets)
		if stats.game_active:

			ship.update()
			gf.update_bullets(ai_settings, screen, stats, sb, ship, \
														aliens, bullets)
			gf.update_aliens(ai_settings, stats, screen, ship, aliens, \
																bullets)
		gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, \
												bullets, play_button)

if __name__ == '__main__':
	run_game()