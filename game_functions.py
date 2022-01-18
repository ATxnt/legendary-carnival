#game_functions.py

import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep


def check_keydown_events(event, ai_settings, screen, ship, bullets):
	"""响应按键"""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		fire_bullet(ai_settings, screen, ship, bullets)
	elif event.key == pygame.K_q:
		sys.exit()


def fire_bullet(ai_settings, screen, ship, bullets):
	"""如果还没有达到限制，就发射一颗子弹"""
	#创建一颗子弹，并将其加入到编组bullets中
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)


def check_keyup_events(event, ship):
	"""响应松开"""
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.key == pygame.K_LEFT:
		ship.moving_left = False


def check_events(ai_settings, screen, stats, play_button, ship, \
													aliens, bullets):
	"""响应按键和鼠标"""
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen,
									 ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, play_button, \
								ship, aliens, bullets, mouse_x, mouse_y)


def check_play_button(ai_settings, screen, stats, play_button, ship, \
									aliens, bullets, mouse_x, mouse_y):
	#单击play按钮开始游戏
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:

		#重置游戏设置
		ai_settings.initialize_dynamic_settings()

		#隐藏光标
		pygame.mouse.set_visible(False)

		#重置统计信息
		stats.reset_stats()
		stats.game_active = True

		#清空子弹和外星人列表
		aliens.empty()
		bullets.empty()

		#创建一群外星人,并让飞船居中
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, \
												bullets, play_button):
	"""更新屏幕"""
	screen.fill(ai_settings.bg_color)
	#在飞船和外星人后面重绘所有子弹
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)


	#显示得分
	sb.show_score()


	#如果游戏处于非活动状态，就绘制play按钮
	if not stats.game_active:
		play_button.draw_button()


	# 让最新绘制的屏幕可见
	pygame.display.flip()
	# draw bullets
	for bullet in bullets.sprites():
		bullet.draw_bullet()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
	"""更新子弹的位置，并删除已消失的子弹"""
	#更新子弹的位置
	bullets.update()

	#删除已消失的子弹
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)

	check_bullet_alien_collisions(ai_settings, screen, stats, sb, \
												ship, aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, \
												ship, aliens, bullets):
	#响应子弹与外星人的碰撞
	#如果是，则删除外星人与子弹
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points * len(aliens)
		stats.score += ai_settings.alien_points
		sb.prep_score()
	check_high_score(stats, sb)

	if len(aliens) == 0:
		#删除现有的子弹，加快游戏节奏，并创建一群新的外星人
		bullets.empty()
		ai_settings.increase_speed()
		create_fleet(ai_settings, screen, ship, aliens)


def get_number_alines_x(ai_settings, alien_width):
	#计算一行能容纳多少外星人
	availble_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(availble_space_x / (2 * alien_width))
	return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
	"""计算屏幕能容纳多少行外星人"""
	availble_space_y = (ai_settings.screen_height - 
		(3 * alien_height) - ship_height)
	number_rows = int(availble_space_y / (2 * alien_height))
	return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, \
		rows_number):
	#创建一个外星人,并放在当前行
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + \
		2 * alien.rect.height * rows_number
	aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
	"""创建外星人群"""	
	#外星人间距为外星人宽度
	#创建一个外星人，并计算一行能容纳多少外星人
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_alines_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height,
		alien.rect.height)


	#创建外星人群
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, alien_number, 
				row_number)


def check_fleet_edges(ai_settings, aliens):
	"""外星人与边缘碰撞时处理"""
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break


def change_fleet_direction(ai_settings, aliens):
	"""将外星人整体下移"""
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
	"""响应被外星人撞到的飞船"""
	if stats.ships_left > 0:
		#将ships_left减1
		stats.ships_left -= 1

		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()

		#创建一群外星人，并将飞船放到屏幕底部中央
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()

		#暂停
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, \
															bullets):
	"""检查是否有外星人到达了屏幕底端"""
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
			break


def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
	"""检查外星人是否在屏幕边缘，碰撞时向左或向右移动"""
	check_fleet_edges(ai_settings, aliens)
	aliens.update()

	#检测外星人和飞船之间的碰撞
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
	check_aliens_bottom(ai_settings, stats, screen, ship, aliens, \
																bullets)

def check_high_score(stats, sb):
	"""检查是否诞生了新的最高得分"""
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()