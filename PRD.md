# PRD: Drill #11 소년 - 자동 무적 런(AutoRun) 상태 추가

## 1. 목표

LEC12 캐릭터 컨트롤러(IDLE / SLEEP / RUN 상태 머신)에 **자동 무적 런(AUTO_RUN)** 상태를 추가한다.
`a` 키를 누르면 소년이 커지고 빨라져서 키 조작 없이 좌우로 계속 달리고, 5초가 지나면 IDLE 로 돌아온다.
기능을 작은 단계로 나눠 개발하고, 단계마다 한국어 메시지로 커밋한다.

## 2. 기본 정보

| 항목 | 내용 |
| --- | --- |
| 도구 | Python 3.13, pico2d 1.5.1, transitions 0.9.3 (`pip install pico2d transitions`) |
| 소스 | `main.py` (게임 루프), `boy.py` (소년·상태 머신), `grass.py` (땅) |
| 이미지 | `animation_sheet.png` (100x100 프레임 8개 x 4줄), `grass.png` |
| 화면 | 800 x 600 |
| 실행 | 이 폴더에서 `python main.py` |

## 3. 기능 요구사항 (과제 조건)

| # | 요구사항 | 상세 | 배점 |
| --- | --- | --- | --- |
| F1 | `a` 키로 AUTO_RUN | IDLE 에서 `a` 를 누르면 AUTO_RUN 이 되어 키 조작 없이 계속 좌우로 이동한다 | 1 |
| F2 | 5초 후 IDLE | AUTO_RUN 에 들어온 지 5초가 지나면 IDLE 로 돌아간다 | 1 |
| F3 | 빨라지고 커짐 | AUTO_RUN 동안 RUN 보다 빠르게 달리고, 그림이 확대된다 | 1 |
| F4 | 끝에서 방향 전환 | 화면 좌우 끝에 닿으면 자동으로 반대 방향으로 달린다 | 1 |
| F5 | 방향키로 취소 | AUTO_RUN 에서 방향키를 누르면 무적 런이 취소되고, 누른 방향으로 움직이는 원래 RUN 이 된다 | - |
| F6 | 상태 클래스 | **반드시 AutoRun 상태 클래스를 추가해서 구현** (과제 중요 조건) | - |
| F7 | 상태 다이어그램 | 상태 다이어그램을 그려 이미지 파일(`state_diagram.png`)로 저장소에 포함 | 1 |

기존 동작(IDLE 5초 → SLEEP, SLEEP 에서 SPACE → IDLE, 방향키 → RUN, 화면 밖으로 안 나감)은 그대로 유지한다.

## 4. 설계

### 4.1 상태와 전이

| 이벤트 (trigger) | 출발 → 도착 | 원인 |
| --- | --- | --- |
| `time_out` | IDLE → SLEEP | IDLE 로 5초 경과 |
| `space_down` | SLEEP → IDLE | SPACE 누름 |
| `run` | IDLE, SLEEP, **AUTO_RUN** → RUN | 방향키 누름 (왼쪽-오른쪽 합이 0 이 아님) |
| `stop` | RUN → IDLE | 방향키 뗌 (합이 0) |
| `a_down` | IDLE → **AUTO_RUN** | `a` 키 누름 |
| `time_out` | **AUTO_RUN** → IDLE | AUTO_RUN 으로 5초 경과 |

AUTO_RUN 안에서 화면 끝에 닿아 방향을 바꾸는 것은 상태가 바뀌지 않는 내부 동작이다.

### 4.2 AutoRun 상태 클래스

`transitions.State` 를 상속한 `AutoRun` 클래스로 만든다. 수업에서 배운 상태의 세 가지 일을 메서드로 나눈다.

| 메서드 | 역할 (수업 용어) | 내용 |
| --- | --- | --- |
| `enter(event_data)` | entry action | 시작 시각 기록, 크기 키우기 |
| `exit(event_data)` | exit action | 크기 원래대로 |
| `do(boy, now, dt)` | do activity | 빠르게 이동, 끝에서 방향 전환, 5초 지나면 `time_out` |
| `draw(boy)` | (그리기) | 확대한 달리기 그림을 발이 땅에 붙게 그림 |

`Boy` 는 `AutoRun('AUTO_RUN')` 객체를 상태 목록에 넣고, AUTO_RUN 일 때 `update` / `draw` 를 이 객체에 맡긴다.

### 4.3 수치

| 이름 | 값 | 근거 |
| --- | --- | --- |
| `AUTO_RUN_TIME` | 5.0 초 | 과제 조건 |
| `AUTO_RUN_SPEED` | `RUN_SPEED` x 2 = 600 px/초 | "속도가 빨라짐" |
| `AUTO_RUN_SCALE` | 2.0 배 | 과제 예시 그림처럼 눈에 띄게 확대 |
| 확대 시 y | 발이 땅에 붙도록 위로 올림 | 달리기 그림의 발은 프레임 중심에서 39px 아래 (실측) |
| 확대 시 화면 여백 | `HALF_WIDTH` x 2 = 64 px | 달리기 그림 몸 끝까지 32px (실측) 의 2배 |

## 5. 개발 단계 (단계마다 커밋)

1. PRD.md 작성
2. AutoRun 상태 클래스 + `a` 키로 진입, 바라보는 방향으로 자동 이동 (F1, F6)
3. 확대·속도 증가, 발이 땅에 붙게 그리기 (F3)
4. 화면 끝에서 방향 전환 (F4)
5. 5초 후 IDLE 복귀 (F2)
6. 방향키로 RUN 전환 (F5)
7. 자동 테스트 추가
8. 상태 다이어그램 이미지와 README 추가 (F7)

## 6. 검증

- `test_boy.py`: 시계(`get_time`)를 가짜로 바꿔 창 없이 상태 전이·이동·경계·5초 타이머를 확인한다.
- 실제 pico2d 로 그린 화면을 캡처해 확대·발 위치·방향 전환을 눈으로 확인한다.
- `python main.py` 로 실행해 오류가 없는지 확인한다.
