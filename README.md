https://github.com/user-attachments/assets/ff6b245d-82bc-4b69-be3b-b8930adfa451

# 🎮 벽돌깨기 (Breakout Game)

> *"벽돌깨기를 한 번도 못해본 사람은 있어도, 결코 한 번만 해본 사람은 없다!"*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![Version](https://img.shields.io/badge/version-1.1-orange.svg)](https://github.com/)


## 📖 프로젝트 소개

**객체 지향 프로그래밍(OOP) 구조**로 설계된 클래식 벽돌깨기 게임입니다. Pygame을 활용하여 제작되었으며, 각 기능을 클래스로 분리하여 **유지보수와 확장이 용이**하도록 구현했습니다.

### ✨ 주요 특징

- 🎯 **직관적인 게임플레이** - 누구나 쉽게 즐길 수 있는 친화형 게임
- 🔧 **OOP 기반 설계** - 클래스 단위로 분리된 깔끔한 코드 구조
- 🎁 **다양한 아이템** - 7가지 파워업으로 전략적 플레이 가능
- 🎵 **사운드 시스템** - 효과음과 배경음악으로 몰입감 증대
- 📊 **실시간 HUD** - 점수, 생명, 공격력, 속도 등 상태 표시

## 🎮 게임 방법

### 조작키

| 키 | 기능 |
|---|------|
| **←/→** | 막대기(Paddle) 좌우 이동 |
| **F** | 총알 발사 (SHOOT 아이템 필요) |
| **Space** | 일시정지 (Pause) |
| **←/→** | 게임 시작 (시작 화면에서) |

### 🎁 아이템 종류

벽돌을 깨뜨리면 랜덤으로 아이템이 등장합니다!

| 아이템 | 효과 | 설명 |
|--------|------|------|
| **[A+]** | 🔺 공격력 강화 | 공의 데미지 증가 |
| **[A-]** | 🔻 공격력 약화 | 공의 데미지 감소 |
| **[S+]** | ⚡ 속도 상승 | 공의 이동 속도 증가 |
| **[S-]** | 🐌 속도 하락 | 공의 이동 속도 감소 |
| **[P+]** | ↔️ 막대 확장 | 패들 길이 증가 |
| **[P-]** | ↕️ 막대 축소 | 패들 길이 감소 |
| **[SH]** | 🔫 총알 발사 | 패들에서 총알 발사 가능 |

### 📊 HUD 정보

화면 상단에 실시간으로 표시되는 정보:
- **Score** - 현재 점수
- **Lives** - 남은 생명
- **ATK** - 공의 공격력
- **Speed** - 공의 속도
- **Shooting** - 총알 발사 모드 여부

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **언어** | Python 3.8+ |
| **게임 엔진** | Pygame |
| **개발 도구** | VSCode |
| **AI 협업** | ChatGPT-5 |
| **설계 패턴** | OOP (Object-Oriented Programming) |

## 📂 프로젝트 구조

```
breakout_game/
├── main.py                 # 게임 실행 파일
├── game.py                 # Game 클래스 (게임 컨트롤러)
├── paddle.py               # Paddle 클래스
├── ball.py                 # Ball 클래스
├── bullet.py               # Bullet 클래스
├── brick.py                # Brick 클래스
├── powerup.py              # PowerUp 클래스
├── level.py                # Level 클래스
├── soundbank.py            # SoundBank 클래스
├── sounds/                 # 효과음 폴더
└── README.md
```

## 🏗️ 핵심 OOP 구조

### 클래스 다이어그램

```
        ┌──────────────┐
        │     Game     │ ◄─── 게임 컨트롤러
        │  (Core)      │
        └──────┬───────┘
               │
    ┌──────────┼──────────────────┐
    │          │                  │
┌───▼───┐  ┌──▼───┐  ┌──────▼────────┐
│Paddle │  │ Ball │  │ Level/Bricks  │
└───────┘  └──┬───┘  └───────────────┘
              │
         ┌────┴────┐
    ┌────▼───┐  ┌─▼──────┐
    │ Bullet │  │PowerUp │
    └────────┘  └────────┘
```

### 주요 클래스 설명

#### 🎯 Game (게임 컨트롤러)
- 전체 게임 흐름을 관리하는 중심 클래스
- 모든 객체를 생성하고 매 프레임마다 업데이트
- `handle_events() → update(dt) → draw()` 흐름 제어
- 점수, 라이프, 아이템 상태 통합 관리

#### 🏓 Paddle (패들)
- 플레이어 입력을 받아 좌우 이동 처리
- `scale_width()`로 패들 크기 조절 (타임드 버프)
- SHOOT 모드 시각적 표시

#### ⚽ Ball (공)
- 방향 벡터 × 속도로 이동 관리
- `damage` 필드로 공격력(ATK) 보유
- 속도 버프 타이머 관리

#### 🔫 Bullet (총알)
- SHOOT 아이템으로 활성화
- 직선 궤도로 벽돌 파괴 가능

#### 🧱 Brick (벽돌)
- HP, 색상, 점수를 가진 타겟 객체
- `hit(damage)` 메서드로 데미지 처리

#### 🎁 PowerUp (아이템)
- 벽돌 파괴 시 드롭
- 패들 충돌 시 효과 적용

#### 🗺️ Level (스테이지)
- 벽돌 배치 및 관리
- `alive_count()`로 클리어 조건 체크

#### 🔊 SoundBank (사운드)
- 효과음 및 BGM 통합 관리
- 상황별 사운드 재생

## 🎵 사운드 출처

### 효과음
- **출처**: [Pixabay - Royalty-free sound effects](https://pixabay.com/sound-effects/)
- 충돌, 파괴, 아이템 획득 등 다양한 효과음

### 배경음악
- **곡명**: Heroes Tonight (feat. Johnning)
- **아티스트**: Janji, Johnning
- **레이블**: NCS Release
- **링크**: [Audio.com](https://audio.com/manish-shirodkar/audio/janji-johnning-heroes-tonight-feat-johnning-ncs-release)

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/breakout-game.git
cd breakout-game
```

### 2. 의존성 설치

```bash
pip install pygame
```

### 3. 게임 실행

```bash
python main.py
```

## 💡 왜 OOP 구조로 설계했는가?

### 📌 핵심 이점

1. **역할 분리** - 각 클래스가 명확한 책임을 가짐
2. **유지보수 용이** - 특정 기능 수정 시 해당 클래스만 변경
3. **확장성** - 새로운 기능 추가가 간단함
4. **코드 가독성** - 게임 로직을 직관적으로 파악 가능

### 🔧 확장 예시

새로운 기능을 추가하려면:

```python
# 1. 새로운 클래스 생성 (예: BossBrick)
class BossBrick(Brick):
    def __init__(self, x, y):
        super().__init__(x, y, hp=10, color=PURPLE)
        
# 2. Level에서 생성
def create_boss_level(self):
    self.bricks.append(BossBrick(300, 100))
    
# 3. Game.update()에서 처리
if isinstance(brick, BossBrick):
    # 보스 벽돌 특수 처리
    pass
```

이처럼 **기존 코드를 최소한만 수정**하여 기능을 확장할 수 있습니다!

## 📌 버전 정보

### v1.1 (Current)

- **v1**: OOP 구조 기반 버전
- **_1**: 유지보수 및 개선 버전

#### 개선 사항
- 코드 리팩토링 및 최적화
- 버그 수정 및 안정성 향상
- 주석 추가로 가독성 개선

## 🎓 학습 포인트

이 프로젝트는 다음을 배우기에 적합합니다:

- ✅ 객체 지향 프로그래밍 (OOP) 실전 적용
- ✅ 게임 루프 및 충돌 처리
- ✅ 이벤트 기반 프로그래밍
- ✅ 타이머 및 버프 시스템 구현
- ✅ 사운드 통합 및 관리
- ✅ Pygame 라이브러리 활용

## 🤝 기여하기

프로젝트 개선에 참여하고 싶으시다면:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 향후 계획

- [ ] 보스 벽돌 추가
- [ ] 다양한 총알 타입
- [ ] 새로운 파워업
- [ ] 난이도 선택 기능
- [ ] 최고 점수 저장 기능
- [ ] 멀티플레이 모드

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 사운드 자료는 각 출처의 라이선스를 따릅니다.

## 👨‍💻 개발자

**ChatGPT-5 활용 프로젝트**

---

⭐ 이 게임이 재미있으셨다면 Star를 눌러주세요!

🎮 Happy Gaming!
