"""
Breakout_oop_ver1_1

Python으로 '벽돌깨기 게임' 만들기 (OOP 구조 기반, VScode 프로그램 + Pygame)
Breakout HP Numbers, Ball ATK HUD, and Shooting Power-up (OOP, user friendly version)

> 사용키

- 시작 : 좌우 방향키 아무거나 누르면 게임 시작.
- 좌우 방향키 : 막대기(Paddle) 좌우 이동.
- F 키 : 막대기에서 총알 발사 -> 벽돌 파괴 가능, [SH] 아이템 필수.
- Space 키 : 일시정지(Pause).

> 아이템 설명 (벽돌을 깨뜨리면 무작위로 아이탬이 나온다.)

- 공의 공격력 강화 : [A+]
- 공의 공격력 약화 : [A-]
- 공의 스피드 상승 : [S+]
- 공의 스피드 하락 : [S-]
- 막대기 길이 확장 : [P+]
- 막대기 길이 축소 : [P-]
- 막대기 총알 발사 : [SH]

  * ATK_UP / ATK_DOWN     : 공의 공격력(지속)
  * PAD_EXPAND / PAD_SHRINK: 패들 길이(타임드)
  * SPD_UP / SPD_DOWN     : 공 속도(타임드)
  * SHOOT                 : 일정 시간 동안 Space로 총알 발사 가능 (쿨다운 적용)

> 참고 사항
- 벽돌: HP가 있음. 벽돌 중앙에 HP 표시 (1 ~ 9)
- 스크린 상단에 HUD 표시: Score, Lives, Ball ATK, Speed, Shooting 남은 시간 표기
- 아이템:
"""

import pygame, sys, random, math

# ───────────────────────────────────────────────────
# 전역 설정/상수
# ───────────────────────────────────────────────────
WIDTH, HEIGHT = 800, 600
FPS = 60

# 색상
BLACK   = (15, 15, 18)
WHITE   = (240, 240, 240)
RED     = (240, 100, 100)
GREEN   = (100, 220, 140)
BLUE    = (90, 150, 255)
YELLOW  = (255, 225, 120)
ORANGE  = (255, 170, 90)
CYAN    = (90, 220, 220)
MAGENTA = (210, 100, 210)
GREY    = (60, 60, 66)

# 파워업 타입
ATK_UP     = "atk_up"
ATK_DOWN   = "atk_down"
PAD_EXPAND = "pad_expand"
PAD_SHRINK = "pad_shrink"
SPD_UP     = "spd_up"
SPD_DOWN   = "spd_down"
SHOOT      = "shoot"        # 새로 추가: 총알 발사 권한 획득 (타임드)

POWERUP_COLORS = {
    ATK_UP: MAGENTA,
    ATK_DOWN: RED,
    PAD_EXPAND: CYAN,
    PAD_SHRINK: YELLOW,
    SPD_UP: GREEN,
    SPD_DOWN: ORANGE,
    SHOOT: (180, 180, 255),
}

# ───────────────────────────────────────────────────
# Paddle (패들)
# ───────────────────────────────────────────────────
class Paddle:
    """플레이어가 좌우로 움직이는 막대. 길이 버프(확장/축소)를 타임드로 관리."""
    def __init__(self, x, y, w=120, h=16, speed=460):
        self.base_width = w
        self.rect = pygame.Rect(x - w//2, y - h//2, w, h)
        self.color = BLUE
        self.speed = speed
        self.scale_timer = 0.0

    def update(self, dt, keys):
        vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += self.speed
        self.rect.x += int(vx * dt)
        self.rect.left  = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, WIDTH)

        # 길이 버프 만료 처리
        if self.scale_timer > 0:
            self.scale_timer -= dt
            if self.scale_timer <= 0:
                cx = self.rect.centerx
                self.rect.width = self.base_width
                self.rect.centerx = cx

    def draw(self, screen, can_shoot=False, font=None):
        """
        패들을 화면에 그림.
        shoot 모드일 때는 붉은색 + 'shoot!' 텍스트 표시.
        """
        # 색상 선택
        draw_color = RED if can_shoot else self.color

        # 패들 그리기
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=6)

        # shoot 모드일 때 텍스트 표시
        if can_shoot and font:
            txt = font.render("SHOOT!", True, WHITE)
            screen.blit(
                txt,
                (
                    self.rect.centerx - txt.get_width() // 2,
                    self.rect.centery - txt.get_height() // 2,
                ),
            )
        else:
            # 항상 표시되는 "Enjoy Python" 문구
            if font:
                enjoy = font.render("Enjoy Python", True, (255, 255, 200))
                screen.blit(
                    enjoy,
                    (
                        self.rect.centerx - enjoy.get_width() // 2,
                        self.rect.centery - enjoy.get_height() // 2 - 1 # 살짝 위로
                    ),
                )    

    def scale_width(self, factor=1.5, duration=10.0):
        """패들 길이를 factor배로 변경(타임드)."""
        self.scale_timer = duration
        new_w = max(60, int(self.base_width * factor))
        cx = self.rect.centerx
        self.rect.width = new_w
        self.rect.centerx = cx
        self.rect.left  = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, WIDTH)

# ───────────────────────────────────────────────────
# Ball (공)
# ───────────────────────────────────────────────────
class Ball:
    """공격력(damage)과 타임드 속도 버프를 가진 공. 방향(단위벡터)×속도(스칼라)로 관리."""
    def __init__(self, x, y, r=9, base_speed=400, damage=1):
        self.x = float(x)
        self.y = float(y)
        self.r = r
        self.color = WHITE

        # 초기 방향(위 대각)
        dir_x = random.choice([-0.8, 0.8])
        dir_y = -1.0
        norm = math.hypot(dir_x, dir_y)
        self.vx = dir_x / norm
        self.vy = dir_y / norm

        self.base_speed = base_speed
        self.min_speed = 250
        self.max_speed = 550

        self.buff_factor = 1.0
        self.buff_timer = 0.0

        self.damage = damage

    def effective_speed(self) -> float:
        spd = self.base_speed * self.buff_factor
        return max(self.min_speed, min(self.max_speed, spd))

    def _apply_effective_speed(self):
        n = math.hypot(self.vx, self.vy)
        if n == 0:
            self.vx, self.vy = 0.0, -1.0
            n = 1.0
        self.vx /= n
        self.vy /= n
        spd = self.effective_speed()
        self.vx *= spd
        self.vy *= spd

    def update(self, dt):
        # 속도 버프 감소
        if self.buff_timer > 0:
            self.buff_timer -= dt
            if self.buff_timer <= 0:
                self.buff_factor = 1.0

        self._apply_effective_speed()

        self.x += self.vx * dt
        self.y += self.vy * dt

        # 벽 반사
        if self.rect.left <= 0 and self.vx < 0:   self.vx *= -1
        if self.rect.right >= WIDTH and self.vx > 0: self.vx *= -1
        if self.rect.top <= 0 and self.vy < 0:    self.vy *= -1

        # 반사 후 속도 유지
        # self._apply_effective_speed()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r*2, self.r*2)

    def set_damage(self, value: int):
        self.damage = max(1, int(value))

    def apply_speed_buff(self, factor: float, duration: float):
        self.buff_factor *= factor
        self.buff_timer = max(self.buff_timer, duration)
        self._apply_effective_speed()

# ───────────────────────────────────────────────────
# Bullet (총알)
# ───────────────────────────────────────────────────
class Bullet:
    """Space로 발사하는 탄. 위로 직진, 벽돌과 충돌 시 사라지며 벽돌 HP 감소."""
    def __init__(self, x, y, w=4, h=10, speed=700, damage=1):
        self.rect = pygame.Rect(x - w//2, y - h, w, h)
        self.speed = speed
        self.damage = max(1, int(damage))
        self.color = (255, 255, 180)

    def update(self, dt):
        self.rect.y -= int(self.speed * dt)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=2)

# ───────────────────────────────────────────────────
# Brick (벽돌)
# ───────────────────────────────────────────────────
class Brick:
    """HP가 0이 되면 제거. draw에서 중앙에 HP 숫자를 렌더링."""
    def __init__(self, rect, hp=2, color=ORANGE, score=10):
        self.rect = pygame.Rect(rect)
        self.max_hp = hp
        self.hp = hp
        self.base_color = color
        self.score = score

    def hit(self, damage: int) -> bool:
        self.hp -= max(1, int(damage))
        return self.hp <= 0

    def draw(self, screen, font_small):
        if self.hp <= 0:
            return
        # 체력 비율로 색 어둡게 -> 피해 표현
        ratio = self.hp / self.max_hp
        r, g, b = self.base_color
        fill = (int(r*ratio), int(g*ratio), int(b*ratio))
        pygame.draw.rect(screen, fill, self.rect, border_radius=4)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 1, border_radius=4)

        # 중앙에 HP 숫자 표시
        txt = font_small.render(str(self.hp), True, BLACK)
        screen.blit(
            txt,
            (self.rect.centerx - txt.get_width() // 2,
             self.rect.centery - txt.get_height() // 2)
        )

# ───────────────────────────────────────────────────
# PowerUp (아이템)
# ───────────────────────────────────────────────────
class PowerUp:
    """벽돌 파괴 시 확률적으로 스폰, 패들과 충돌 시 효과 발동."""
    SYMBOLS = {
        ATK_UP: "A+",
        ATK_DOWN: "A-",
        PAD_EXPAND: "P+",
        PAD_SHRINK: "P-",
        SPD_UP: "S+",
        SPD_DOWN: "S-",
        SHOOT: "SH",
    }

    def __init__(self, x, y, kind=ATK_UP):
        self.kind = kind
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.vy = 160
        self.font = pygame.font.SysFont("arial", 14, bold=True)

    def update(self, dt):
        self.rect.y += int(self.vy * dt)

    def draw(self, screen):
        # 사각형 박스
        pygame.draw.rect(screen, POWERUP_COLORS[self.kind], self.rect, border_radius=6)
        pygame.draw.rect(screen, GREY, self.rect, 2, border_radius=6)

        # 종류별 문자 표시
        text = self.SYMBOLS.get(self.kind, "?")
        txt_surface = self.font.render(text, True, BLACK)
        screen.blit(
            txt_surface,
            (
                self.rect.centerx - txt_surface.get_width() // 2,
                self.rect.centery - txt_surface.get_height() // 2,
            ),
        )

# ───────────────────────────────────────────────────
# Level (정사각형 벽돌, 5행, 좌우 2열 제거)
# ───────────────────────────────────────────────────
class Level:
    def __init__(self, rows=5, top=80, vgap=6, size=28, hp=2):
        """
        rows : 벽돌 줄 수 (기본 5)
        top  : 화면 상단 여백
        vgap : 줄 간격(세로)
        size : 정사각형 한 변의 길이(px)
        hp   : 벽돌의 체력
        """
        self.bricks = []
        palette = [ORANGE, GREEN, CYAN, MAGENTA, YELLOW, RED]

        # ─────────────────────────────
        # 가로 배치 계산
        # ─────────────────────────────
        hgap = 3  # 가로 간격
        total_width = WIDTH
        cols = (total_width + hgap) // (size + hgap)
        left = (WIDTH - (cols * size + (cols - 1) * hgap)) // 2  # 중앙 정렬

        # ─────────────────────────────
        # 벽돌 생성
        # ─────────────────────────────
        for r in range(rows):
            for c in range(cols):
                # 왼쪽 2열과 오른쪽 2열은 건너뛴다
                if c < 2 or c >= cols - 2:
                    continue

                x = left + c * (size + hgap)
                y = top + r * (size + vgap)

                # HP를 1~9 랜덤으로 설정
                hp_val = random.randint(1, 9)
                # # 행마다 다른 체력/색상
                # hp_val = 1 if r < 2 else (2 if r < 4 else 3)
                color = palette[r % len(palette)]
                score = 10 * hp_val

                self.bricks.append(
                    Brick((x, y, size, size), hp=hp_val, color=color, score=score)
                )

    def draw(self, screen, font_small):
        for b in self.bricks:
            if b.hp > 0:
                b.draw(screen, font_small)

    def alive_count(self):
        return sum(1 for b in self.bricks if b.hp > 0)

# ───────────────────────────────────────────────────
# SoundBank : 효과음 로더/플레이어
# ───────────────────────────────────────────────────
class SoundBank:
    def __init__(self):
        # mixer 초기화 (이미 init돼 있으면 예외 없이 넘어감)
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            pass

        def load(path, vol=0.8):
            try:
                s = pygame.mixer.Sound(path)
                s.set_volume(vol)
                return s
            except Exception as e:
                print(f"사운드 로드 실패: {path} ({e})")
                return None

        # 원하는 볼륨으로 개별 세팅
        self.paddle_thud  = load("./sfx/paddle_thud.wav", 0.55)
        self.brick_ping   = load("./sfx/brick_ping.wav",  0.45)
        self.brick_break  = load("./sfx/brick_break.wav", 0.70)
        self.game_over    = load("./sfx/game_over.wav",   0.75)
        self.item_get     = load("./sfx/item_get.wav",    3.0)
        self.shoot_fire   = load("./sfx/shoot_fire.wav",  0.5)
        self.stage_clear  = load("./sfx/clear_victory.wav", 0.8)
        self.bgm_path     = load("./bgm/Heroes_Tonight.mp3", 0.5)

    def play(self, sound_obj):
        if sound_obj:
            sound_obj.play()

    # ── BGM 제어 ─────────────────────────────────────
    def play_bgm(self, path=None, volume=0.35, fade_ms=800):
        try:
            if path:
                self.bgm_path = path
            pygame.mixer.music.load(self.bgm_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=-1, fade_ms=fade_ms)  # 무한 반복
        except Exception as e:
            print(f"BGM 재생 실패: {self.bgm_path} ({e})")

    def pause_bgm(self):
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"BGM 일시정지 실패: {e}")

    def resume_bgm(self):
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"BGM 재개 실패: {e}")

    def stop_bgm(self, fade_ms=600):
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception as e:
            print(f"BGM 정지 실패: {e}")

# ───────────────────────────────────────────────────
# Game (전체)
# ───────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Breakout – HP Numbers & Shooting (OOP)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # pygame.init() 이전에 PowerUp() 객체가 생성되면 오류 발생.
        # 현재는 pygame.init()이 Game.__init__에서 먼저 호출되므로 문제는 없음.
        # 다른 파일에서 PowerUp만 테스트할 경우를 대비해 pygame.font.get_init() 체크 추가 권장:
        if not pygame.font.get_init():
            pygame.font.init()

        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16, bold=True)
        self.big  = pygame.font.SysFont("arial", 46, bold=True)

        # 이탤릭 폰트 추가
        self.font_italic = pygame.font.SysFont("arial", 20, italic=True)

        # 배경 이미지 로드
        try:
            bg_img = pygame.image.load("./ilsan.jpg")   # 파일명 확인
            self.bg = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        except Exception as e:
            print("배경 이미지를 불러오지 못했습니다:", e)
            self.bg = None  # 배경이 없을 경우 대비

        # 사운드
        self.sfx = SoundBank()
        self.sfx.play_bgm(path="bgm/Heroes_Tonight.mp3", volume=0.35)  # 🎵 게임 시작 → 재생

        # 먼저 슈팅 관련 속성들을 "존재하게" 만들어 둡니다.
        self.can_shoot = False
        self.shoot_timer = 0.0
        self.shoot_cooldown = 0.0
        self.shoot_interval = 0.25
        self.bullets = []   # <-여기가 중요!
        self.bullet_damage = 1

        # 그 다음에 reset() 호출
        self.reset()

        # 아이템 효과를 적용하는 단일 진입점
    def apply_powerup(self, p):

        # ── 1) 종류별 효과
        if p.kind == ATK_UP:
            self.ball.set_damage(self.ball.damage + 1)
        elif p.kind == ATK_DOWN:
            self.ball.set_damage(self.ball.damage - 1)
        elif p.kind == PAD_EXPAND:
            self.paddle.scale_width(factor=1.6, duration=10.0)
        elif p.kind == PAD_SHRINK:
            self.paddle.scale_width(factor=0.7, duration=10.0)
        elif p.kind == SPD_UP:
            self.ball.apply_speed_buff(factor=1.25, duration=8.0)
        elif p.kind == SPD_DOWN:
            self.ball.apply_speed_buff(factor=0.75, duration=8.0)
        elif p.kind == SHOOT:
            # 슈팅 권한 부여/연장
            self.can_shoot = True
            self.shoot_timer = max(self.shoot_timer, 10.0)

        # ── 2) 공통: 사운드
        self.sfx.play(self.sfx.item_get)

    def reset(self):
        self.paddle = Paddle(WIDTH // 2, HEIGHT - 40)
        self.ball   = Ball(WIDTH // 2, HEIGHT - 80, r=9, base_speed=340, damage=1)
        self.level  = Level()
        self.powerups = []
        self.score  = 0
        self.lives  = 3
        self.paused = False
        self.game_over = False
        self.clear  = False

        # 슈팅 상태 초기화
        # 이미 __init__에서 속성이 존재하므로 여기선 값만 재설정
        self.can_shoot = False
        self.shoot_timer = 0.0
        self.shoot_cooldown = 0.0
        self.bullets = []          # reassign (clear보다 안전)
        self.bullet_damage = 1
        # 공을 패들에 붙여 시작
        self.ball_stuck = True

    # 공-사각형 반사 (면 추정)
    def reflect_ball_from_rect(self, rect: pygame.Rect):
        b = self.ball.rect
        dx_left   = b.right - rect.left
        dx_right  = rect.right - b.left
        dy_top    = b.bottom - rect.top
        dy_bottom = rect.bottom - b.top
        if min(dx_left, dx_right) < min(dy_top, dy_bottom):
            self.ball.vx *= -1
        else:
            self.ball.vy *= -1
        self.ball._apply_effective_speed()

    def handle_events(self):
        for ev in pygame.event.get():
            
            if ev.type == pygame.QUIT:
                self.sfx.stop_bgm()   # 게임 종료 → 음악 종료
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.sfx.stop_bgm()  # 게임 종료 → 음악 종료
                    pygame.quit(); sys.exit()

                # Space 키 = Pause (게임오버/클리어가 아닐 때만)
                if ev.key == pygame.K_SPACE:
                    if not (self.game_over or self.clear):
                        self.paused = not self.paused
                        # Pause일 때만 BGM 일시정지, 해제 시 재개
                        if self.paused:
                            self.sfx.pause_bgm()
                        else:
                            self.sfx.resume_bgm()

                # F 키 = Shoot (즉시 한 발 발사; 연사는 update()에서 처리)
                if ev.key == pygame.K_f:
                    if self.can_shoot and not (self.game_over or self.clear):
                        self.try_fire_bullet()

                # R 키 = 재시작
                if ev.key == pygame.K_r and (self.game_over or self.clear):
                    self.reset()

    def try_fire_bullet(self):
        """쿨다운을 고려하여 탄 1발 발사."""
        if self.shoot_cooldown > 0: 
            return
        # 패들 중앙 상단에서 발사
        bx = self.paddle.rect.centerx
        by = self.paddle.rect.top
        self.bullets.append(Bullet(bx, by, damage=self.bullet_damage))
        self.shoot_cooldown = self.shoot_interval
        # 총알 발사 사운드
        self.sfx.play(self.sfx.shoot_fire)

    def launch_ball(self, dir_sign: int):
        """
        dir_sign: -1(왼쪽 발사), +1(오른쪽 발사)
        초기 각도를 살짝 비스듬하게 주고 현재 속도로 가속 적용
        """
        # 살짝 비스듬한 각도
        dir_x = -0.75 if dir_sign < 0 else 0.75
        dir_y = -1.0
        n = math.hypot(dir_x, dir_y)
        self.ball.vx = dir_x / n
        self.ball.vy = dir_y / n
        # 현재 유효 속도로 스케일링
        self.ball._apply_effective_speed()
        self.ball_stuck = False    

    def update(self, dt):
        if self.paused or self.game_over or self.clear:
            return

        keys = pygame.key.get_pressed()
        self.paddle.update(dt, keys)


        # 공이 패들에 붙어있는 동안: 패들을 따라다님 + 방향키 입력 시 발사
        if getattr(self, "ball_stuck", False):
            # 공 위치를 패들 중앙 위에 고정
            self.ball.x = self.paddle.rect.centerx
            self.ball.y = self.paddle.rect.top - self.ball.r - 1  # 살짝 겹치지 않게 -1

            # ←/→ 또는 A/D 누를 때 발사
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.launch_ball(-1)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.launch_ball(+1)
            else:
                # 아직 발사 전이면, 나머지 업데이트는 건너뜀
                return
        else:
            # 평소처럼 공 물리 업데이트
            self.ball.update(dt)
            

        # 연사: F 키를 누르고 있고, SHOOT 가능하면 쿨다운에 맞춰 자동 발사
        if self.can_shoot and keys[pygame.K_f]:
            self.try_fire_bullet()

        # 슈팅 쿨다운/타이머 감소
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.can_shoot:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.can_shoot = False

        # 패들-공 충돌 (각도 조정 + 위로 반사)
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.vy > 0:
            offset = (self.ball.x - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
            dir_x = max(-1.0, min(1.0, offset))
            dir_y = -1.0
            n = math.hypot(dir_x, dir_y)
            self.ball.vx, self.ball.vy = (dir_x / n), (dir_y / n)
            self.ball._apply_effective_speed()
            # 패들 둔탁 사운드
            self.sfx.play(self.sfx.paddle_thud)

        # 벽돌 충돌 (공)
        for b in list(self.level.bricks):
            if b.hp > 0 and self.ball.rect.colliderect(b.rect):
                self.reflect_ball_from_rect(b.rect)
                destroyed = b.hit(self.ball.damage)

                # 벽돌 히트(유리 ‘팅’)
                self.sfx.play(self.sfx.brick_ping)

                if destroyed:
                    self.score += b.score

                    # 벽돌 파괴(유리 깨짐)
                    self.sfx.play(self.sfx.brick_break)


                    # 아이템 드랍 (확률)
                    if random.random() < 0.4:
                        kind = random.choices(
                            [ATK_UP, ATK_DOWN, PAD_EXPAND, PAD_SHRINK, SPD_UP, SPD_DOWN, SHOOT],
                            weights=[3,2,3,2,3,2,3], k=1
                        )[0]
                        self.powerups.append(PowerUp(b.rect.centerx, b.rect.centery, kind))

        # 총알 이동/충돌
        for bullet in list(self.bullets):
            bullet.update(dt)
            # 화면 밖 제거
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
                continue
            # 벽돌과 충돌 체크 (한 발은 한 벽돌만 타격하고 소멸)
            hit_any = False
            for b in self.level.bricks:
                if b.hp > 0 and bullet.rect.colliderect(b.rect):
                    destroyed = b.hit(bullet.damage)
                    hit_any = True
                    if destroyed:
                        self.score += b.score
                        # 총알로 파괴해도 아이템 드랍 가능
                        if random.random() < 0.25:
                            kind = random.choices(
                                [ATK_UP, ATK_DOWN, PAD_EXPAND, PAD_SHRINK, SPD_UP, SPD_DOWN, SHOOT],
                                weights=[3,2,3,2,3,2,3], k=1
                            )[0]
                            self.powerups.append(PowerUp(b.rect.centerx, b.rect.centery, kind))
                    break
            if hit_any:
                self.bullets.remove(bullet)

        # 아이템 업데이트/획득  ✅ 이 블록만 유지
        new_list = []
        for p in self.powerups:
            p.update(dt)
            if p.rect.top > HEIGHT:
                continue  # 화면 밖으로 나간 아이템은 버림

            if p.rect.colliderect(self.paddle.rect.inflate(10, 6)):
                # 패들과 닿으면 적용하고 목록에 넣지 않음(= 제거)
                self.apply_powerup(p)
            else:
                new_list.append(p)

        self.powerups = new_list

        # 공이 바닥으로 떨어지면 라이프 감소
        if self.ball.rect.top > HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                # 게임오버
                self.sfx.play(self.sfx.game_over)
            else:
                # 공/패들만 소프트 리셋 (공격력/아이템 상태는 유지/만료 로직대로)
                self.paddle = Paddle(WIDTH // 2, HEIGHT - 40)
                self.ball   = Ball(WIDTH // 2, HEIGHT - 80, r=9, base_speed=340, damage=self.ball.damage)
                # 슈팅은 계속 남아있지만 shoot_timer가 남은 만큼만 유지
                self.bullets.clear()
                self.shoot_cooldown = 0.0
                # 다시 패들에 붙인 상태로
                self.ball_stuck = True

        # 스테이지 클리어
        if self.level.alive_count() == 0:
            if not self.clear:  # 처음 클리어될 때만 재생
                self.clear = True
                self.sfx.play(self.sfx.stage_clear)  # 축하 사운드 재생

    def draw_hud(self):
        # 각 항목을 렌더링
        s = self.font.render(f"Score: {self.score}", True, WHITE)
        l = self.font.render(f"Lives: {self.lives}", True, WHITE)
        d = self.font.render(f"ATK: {self.ball.damage}", True, WHITE)
        v = self.font.render(f"Speed: {int(self.ball.effective_speed())}", True, WHITE)

        # SHOOT 남은 시간 표기
        if self.can_shoot:
            t = max(0, int(self.shoot_timer))
            shoot_text = self.font.render(f"Shoot ON ({t}s)", True, (180, 220, 255))
        else:
            shoot_text = self.font.render("Shoot OFF", True, (180, 180, 200))


        # 가로로 배치 — x 좌표를 오른쪽으로 조금씩 이동
        spacing = 10  # 각 항목 사이 여백
        x = 10
        y = 8

        for txt in [s, l, d, v, shoot_text]:
            self.screen.blit(txt, (x, y))
            x += txt.get_width() + spacing  # 다음 텍스트는 오른쪽으로 이동

        # 상단 오른쪽 안내문 추가
        guide_text = self.font_small.render("Press keys | [Space] : Pause, [F] : Shoot", True, (220, 220, 220))
        # 오른쪽 끝 정렬 (10px 여백)
        guide_x = WIDTH - guide_text.get_width() - 10
        guide_y = 12
        self.screen.blit(guide_text, (guide_x, guide_y))

        # 일시정지, 게임오버, 클리어 메시지는 그대로 유지
        if self.paused:
            t = self.big.render("PAUSED", True, WHITE)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 30))

        if self.game_over:
            t = self.big.render("GAME OVER", True, RED)
            h = self.font.render("Press R to Restart, ESC to Quit", True, WHITE)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
            self.screen.blit(h, (WIDTH//2 - h.get_width()//2, HEIGHT//2 + 10))

        if self.clear:
            t = self.big.render("STAGE CLEAR!", True, GREEN)
            h = self.font.render("Press R to Play Again, ESC to Quit", True, WHITE)
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
            self.screen.blit(h, (WIDTH//2 - h.get_width()//2, HEIGHT//2 + 10))

    def draw(self):
        # 배경 이미지 (ilsan.jpg)
        if hasattr(self, "bg") and self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill(BLACK)
        self.level.draw(self.screen, self.font_small)

        # 아이템, 패들, 공, 총알 순으로 그리기
        for p in self.powerups:
            p.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        self.paddle.draw(self.screen, can_shoot=self.can_shoot, font=self.font_small)
        self.ball.draw(self.screen)

        # HUD (점수, 라이프 등)
        self.draw_hud()

        # 항상 표시되는 배경 음악 제목
        song_text = self.font_italic.render("Song : Heros Tonight - Lyrics", True, (180, 180, 220))
        song_x = WIDTH // 2 - song_text.get_width() // 2   # 가운데 정렬
        song_y = HEIGHT - song_text.get_height() - 12      # 화면 아래에서 12px 위
        self.screen.blit(song_text, (song_x, song_y))

        # 화면 갱신
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()


# ───────────────────────────────────────────────────
# main
# ───────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()


# 실행 방법
# cmd 에서 python breakout_oop.py 실행
# 또는 breakout_oop.py 현재 창에 커서를 띄우고 ctrl + enter
