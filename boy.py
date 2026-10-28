import math

from pico2d import (load_image, get_time, get_canvas_width,
                    SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a)
from transitions import Machine, State

SLEEP_WAIT_TIME = 5.0  # IDLE 상태로 이 시간(초)이 지나면 SLEEP 으로 간다.
LIE_DOWN_TIME = 0.6    # 눕거나 일어나는 데 걸리는 시간(초)
QUICK_GET_UP_TIME = 0.2  # 달리려고 벌떡 일어나는 데 걸리는 시간(초)
RUN_SPEED = 300        # 달리기 속도(픽셀/초)
HALF_WIDTH = 32        # 그림 중심에서 몸 끝까지 가로 거리 (달리기 스프라이트 실측값)

# 회전 중심 = 발뒤꿈치. 그림 중심에서 뒤쪽으로 4px, 아래로 38px (스프라이트 실측값)
# 뒤꿈치를 축으로 넘어지면 발은 땅에 붙은 채로, 누웠을 때 등이 땅에 닿는다.
HEEL_DX, HEEL_DY = 4, 38


class AutoRun(State):
    """자동 무적 런: a 키로 들어와 키 조작 없이 계속 달린다."""

    # entry action
    def enter(self, event_data):
        boy = event_data.model
        boy.lie = 0.0  # 일어나는 도중에 들어와도 바로 선 자세로 달린다.
        super().enter(event_data)

    # do activity: 매 프레임 바라보는 방향으로 달린다.
    def do(self, boy, now, dt):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.face_dir * RUN_SPEED * dt
        boy.x = max(HALF_WIDTH, min(get_canvas_width() - HALF_WIDTH, boy.x))

    def draw(self, boy):
        bottom = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(boy.frame * 100, bottom, 100, 100, boy.x, boy.y)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1  # 1 = 오른쪽, -1 = 왼쪽
        self.image = load_image('animation_sheet.png')

        # 지금 눌려 있는 방향키. 둘을 따로 기억해야 한쪽만 뗐을 때를 처리할 수 있다.
        self.left_pressed = False
        self.right_pressed = False

        # 0.0 = 서 있음, 1.0 = 완전히 누움. 상태에 따라 서서히 변한다.
        self.lie = 0.0
        self.last_time = get_time()

        # 초기 상태 진입 시에는 on_enter_IDLE 이 호출되지 않으므로 직접 타이머를 시작한다.
        self.wait_start_time = get_time()

        # AUTO_RUN 은 할 일이 많아서 상태 클래스(AutoRun)로 만든다.
        self.auto_run = AutoRun('AUTO_RUN')

        # IDLE --time_out--> SLEEP --space_down--> IDLE
        # IDLE, SLEEP --run--> RUN --stop--> IDLE  (왼쪽/오른쪽은 move_dir 로 구분)
        # IDLE --a_down--> AUTO_RUN
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', self.auto_run],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'a_down', 'source': 'IDLE', 'dest': 'AUTO_RUN'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,  # 해당 상태에 없는 이벤트는 무시 (예: IDLE 에서 SPACE)
        )

    # IDLE 로 돌아올 때마다 5초 타이머를 다시 시작한다.
    def on_enter_IDLE(self):
        self.wait_start_time = get_time()

    # 눌린 방향키로 이동 방향을 구한다. 둘 다 눌렸거나 둘 다 안 눌렸으면 0.
    def move_dir(self):
        return int(self.right_pressed) - int(self.left_pressed)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.space_down()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_a:
            self.a_down()
        elif event.type in (SDL_KEYDOWN, SDL_KEYUP) and event.key in (SDLK_LEFT, SDLK_RIGHT):
            pressed = event.type == SDL_KEYDOWN
            if event.key == SDLK_LEFT:
                self.left_pressed = pressed
            else:
                self.right_pressed = pressed

            if self.move_dir() != 0:
                self.run()
            else:
                self.stop()

    def update(self):
        now = get_time()
        dt = now - self.last_time
        self.last_time = now

        # SLEEP 이면 누운 쪽(1.0)으로, 아니면 선 쪽(0.0)으로 조금씩 움직인다.
        # 달리려고 일어날 때(RUN)는 SPACE 로 깰 때보다 빠르게 일어난다.
        if self.state == 'SLEEP':
            self.lie = min(1.0, self.lie + dt / LIE_DOWN_TIME)
        elif self.state == 'RUN':
            self.lie = max(0.0, self.lie - dt / QUICK_GET_UP_TIME)
        else:
            self.lie = max(0.0, self.lie - dt / LIE_DOWN_TIME)

        if self.state == 'IDLE':
            # 자는 동안과 일어나는 도중에는 움직이지 않고, 다 일어선 뒤부터 움직인다.
            if self.lie == 0.0:
                self.frame = (self.frame + 1) % 8
            if now - self.wait_start_time >= SLEEP_WAIT_TIME:
                self.time_out()
        elif self.state == 'RUN' and self.lie == 0.0:  # 다 일어선 뒤부터 달린다.
            self.frame = (self.frame + 1) % 8
            self.face_dir = self.move_dir()
            self.x += self.face_dir * RUN_SPEED * dt
            # 화면 밖으로 나가지 않게 막는다.
            self.x = max(HALF_WIDTH, min(get_canvas_width() - HALF_WIDTH, self.x))
        elif self.state == 'AUTO_RUN':
            self.auto_run.do(self, now, dt)

    def draw(self):
        if self.state == 'AUTO_RUN':
            self.auto_run.draw(self)
            return

        if self.state == 'RUN' and self.lie == 0.0:
            # 아래에서 두 번째 줄(100)은 오른쪽, 맨 아랫줄(0)은 왼쪽으로 달린다.
            bottom = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, bottom, 100, 100, self.x, self.y)
            return

        # 맨 윗줄(300)은 오른쪽, 그 아래(200)는 왼쪽을 보고 서 있다.
        bottom = 300 if self.face_dir == 1 else 200

        # 제곱을 써서 처음엔 천천히, 끝에선 빠르게 넘어지도록 한다.
        angle = (math.pi / 2) * self.lie * self.lie

        # 발뒤꿈치를 축으로 그림 중심을 회전시킨다. (angle 0 이면 원래 위치)
        # 왼쪽을 보면 좌우가 뒤집히므로 x 이동과 회전 방향에 face_dir 를 곱한다.
        c, s = math.cos(angle), math.sin(angle)
        cx = self.x + self.face_dir * (-HEEL_DX + HEEL_DX * c - HEEL_DY * s)
        cy = self.y - HEEL_DY + HEEL_DX * s + HEEL_DY * c
        self.image.clip_composite_draw(self.frame * 100, bottom, 100, 100,
                                       self.face_dir * angle, '', cx, cy, 100, 100)
