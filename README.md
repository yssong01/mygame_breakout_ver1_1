https://github.com/user-attachments/assets/ff6b245d-82bc-4b69-be3b-b8930adfa451

## [게임] 벽돌깨기 (Breakout)

벽돌깨기를 한 번도 못해본 사람은 있어도, 결코 한 번만 해본 사람은 없다!


### 1. 게임 소개 및 프로젝트 개요

> 이 프로젝트는 ChatGPT5를 활용하여 VScode program을 이용하여 Pygame으로 만든 오브젝트 지향 프로그래밍(OOP) 구조에 기반한 벽돌깨기 게임입니다.

- 각 기능을 클래스(Class)로 분리하여 수정(유지보수)와 확장(버전업)이 쉽도록 설계했습니다.

> 누구나 쉽게 접근할 수 있는 친화형 게임입니다.

- 막대기(Paddle)를 좌우로 움직이면서 공을 받아 쳐내어 벽돌을 깨뜨리는 단순하지만 stage clear를 위해서 적당한 집중력이 필요한 게임입니다.
- 공의 공격력(ATK), 공의 속도(SPD), 막대기 크기, 벽돌의 hp, 아이템 회득, 막대기의 총알 발사(SHOOT)에 변화를 주는 아이템 획득 기능과 효과음, 배경음을 추가하여 재미를 더하였습니다.


### 2. 게임 방법

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

> 스크린 상단에 HUD 표시

- Score, Lives, ATK, Speed, Shooting의 현재 상태


### 3. 효과음, 배경음

> 효과음 출처 : Royalty-free sound effects for download

- https://pixabay.com/sound-effects/?utm_source=chatgpt.com

> 배경음 출처 : Janji, Johnning - Heroes Tonight (feat. Johnning) [NCS Release]

- https://audio.com/manish-shirodkar/audio/janji-johnning-heroes-tonight-feat-johnning-ncs-release


### 4. 핵심 OOP 구조를 기반으로 게임을 구현.

이 게임의 전체 구조는 Game class가 중심(core) 역할로서 모든 객체를 생성하고, 각 클래스는 자신의 역할만 책임지는 구조입니다. 따라서 이러한 OOP 설계 덕분에, 현재 없는 기능인 “보스 벽돌” 같은 새로운 클래스를 추가하더라도
Level과 Game.update() 일부에서만 수정하면 손쉽게 게임 기능 확장이 가능합니다.

> Game

- 전체 게임을 관리하는 컨트롤러 클래스입니다.
- Paddle, Ball, Level, SoundBank 인스턴스를 생성하고, 매 프레임마다 handle_events() → update(dt) → draw() 흐름으로 호출합니다.
- Shoot, 아이템, 점수, 라이프 상태를 모두 한 곳에서 통합 관리합니다.

> Paddle (패들)

- 플레이어 입력(←→ / A D)을 받아 update()에서 좌우 이동을 처리합니다.
- scale_width()로 패들 길이를 일정 시간 확장/축소하는 타임드 버프를 관리합니다.
- draw()에서 Shoot 모드일 때는 빨간 패들 + "SHOOT!", 기본 상태에서는 "Enjoy Python" 텍스트를 패들 위에 표시합니다.
- Game은 self.paddle.update(), self.paddle.draw()를 호출해 동작시킵니다.

> Ball (공)

- 방향(단위 벡터) × 속도(스칼라)로 속도를 관리하는 클래스입니다.
- damage 필드를 통해 공의 공격력(ATK) 을 갖고 있고, set_damage()로 아이템 효과에 따라 증감시킵니다.
- apply_speed_buff()로 속도 버프를 주면, buff_timer로 남은 시간을 관리합니다.
- Game은 ball.update(dt)로 이동을 갱신하고, 벽/패들/벽돌 충돌 시 reflect_ball_from_rect()와 Brick.hit()를 호출합니다.

> Bullet (총알)

- SHOOT 아이템으로 활성화되는 직선 탄환입니다.
- Game.try_fire_bullet()에서 패들 위치를 기준으로 생성되며,
  bullets 리스트에 모아 update() → draw() → 벽돌 충돌 체크를 합니다.

> Brick (벽돌)

- 위치, hp, 색상, 점수를 가지는 단순한 데이터 + 로직 클래스입니다.
- hit(damage)는 HP를 감소시키고, 파괴되면 True를 반환하여
  Game이 점수 증가 및 아이템 드랍 여부를 판단하도록 합니다.

> PowerUp (아이템)

- 벽돌 파괴 시 Game에서 생성하며, 아래로 떨어지는 상자입니다.
- 패들과 충돌하면 Game.apply_powerup()을 호출해
  ATK 변경, 패들 길이 변경, 공 속도 변경, Shoot 모드 활성화를 적용합니다.

> Level (스테이지)

- 여러 개의 Brick을 생성하고 리스트로 관리하는 클래스입니다.
- alive_count()로 남아있는 벽돌 개수를 세어서, 스테이지 클리어 여부를 판단합니다.

> SoundBank (사운드 관리)

- 효과음과 BGM을 로드하고, play() / play_bgm() / pause_bgm() 등으로 재생합니다.
- Game에서 충돌, 파괴, 아이템 획득, 게임오버, 클리어 등 상황별로 호출합니다.


### 5. Summary : 왜 이러한 OOP 구조로 게임을 구현했는가?

> 게임의 전체 기능이 정상적으로 수행되도록 각 클래스의 역할을 '구분'하고 또한 서로 method call로 연결되도록 하여 클래스의 수정, 추가, 확장 등의 작업이 용이하도록 하였다.

- 각 클래스의 기능들, 즉 게임 규칙(언제 점수를 올릴지, 언제 아이템을 줄지, 언제 게임오버 등)이 Game 클래스에서 코드 작동을 파악하기 용이합니다.
- 이는 유지보수 및 버전 업 작업에 유리한 장기적인 안목을 반영하는 연습을 할 수 있는 좋은 예제로써, 즉 앞으로 새로운 기능(보스 벽돌, 다른 종류의 총알, 새로운 파워업 등)을 추가할 때도 관련 클래스를 추가/확장하고 Game.update()와 apply_powerup() 등 에서만 최소한으로 method call하여 연결해 주면 됩니다.

#6. Version : ver1_1

- 'ver1' : oop구조의 버전을 의미합니다.
- '\_1' : oop구조에서의 유지보수된 버전을 의미합니다.
