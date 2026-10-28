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

## 7. 구현 결과

계획한 단계대로 모두 구현했다. 단계마다 커밋했고, 개발 단계 5 의 1 ~ 8 외에 다른 폴더에서 실행해도
이미지를 찾도록 작업 폴더를 옮기는 커밋을 하나 더 넣었다.

| 요구사항 | 결과 | 확인 방법 |
| --- | --- | --- |
| F1 `a` 키로 AUTO_RUN | 완료 | `test_a_key_starts_auto_run_without_arrow_keys`, `test_a_key_only_from_idle` |
| F2 5초 후 IDLE | 완료 (IDLE 수면 타이머도 재시작) | `test_back_to_idle_after_5_seconds` |
| F3 빨라지고 커짐 | 완료 (속도 2배, 크기 2배, 끝나면 원래 크기) | `test_faster_and_bigger`, `test_size_back_to_normal_after_auto_run`, 렌더링 캡처로 발끝 높이 확인 |
| F4 끝에서 방향 전환 | 완료 (커진 몸도 화면 안) | `test_turns_around_at_both_edges`, 렌더링 캡처로 양쪽 끝 확인 |
| F5 방향키로 취소 | 완료 | `test_arrow_cancels_auto_run` |
| F6 AutoRun 상태 클래스 | 완료 (`class AutoRun(transitions.State)`) | 테스트에서 상태 객체가 `AutoRun` 인지 확인 |
| F7 상태 다이어그램 | 완료 (`state_diagram.png`) | README 에 삽입 |

### 검증 결과

- `python test_boy.py`: 16개 모두 통과 (기존 IDLE/SLEEP/RUN 8개 + AutoRun 8개)
- 실제 pico2d 렌더링: AUTO_RUN 소년이 2배 크기로 그려지고, 발끝이 보통 크기일 때와 같은 땅 높이에 있으며,
  화면 왼쪽 끝(x=64)·오른쪽 끝(x=736)에서도 몸이 잘리지 않음
- `python main.py`: 오류 없이 실행

### 개발 중 발견한 문제

- 테스트 도우미 `run_until` 이 0.01초씩 더하다 생긴 부동소수점 오차로 마지막 시각(정확히 5.0초)을 건너뛰어,
  5초 타이머 테스트 3개가 실패했다. 코드가 아니라 테스트 문제였고, 마지막 걸음을 정확히 목표 시각에 맞추도록 고쳤다.
- 상위 폴더에서 `python DRILL11/main.py` 로 실행하면 이미지를 못 찾아 `OSError` 가 났다. 작업 폴더를 소스 위치로 옮겨 해결했다.
