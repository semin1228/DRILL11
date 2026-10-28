import math

from pico2d import load_image, get_time, SDL_KEYDOWN, SDLK_SPACE
from transitions import Machine

SLEEP_WAIT_TIME = 5.0  # IDLE 상태로 이 시간(초)이 지나면 SLEEP 으로 간다.
LIE_DOWN_TIME = 0.6    # 눕거나 일어나는 데 걸리는 시간(초)
# 회전 중심 = 발뒤꿈치. 그림 중심에서 왼쪽으로 4px, 아래로 38px (스프라이트 실측값)
# 뒤꿈치를 축으로 넘어지면 발은 땅에 붙은 채로, 누웠을 때 등이 땅에 닿는다.
HEEL_DX, HEEL_DY = 4, 38


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.image = load_image('animation_sheet.png')

        # 0.0 = 서 있음, 1.0 = 완전히 누움. 상태에 따라 서서히 변한다.
        self.lie = 0.0
        self.last_time = get_time()

        # 초기 상태 진입 시에는 on_enter_IDLE 이 호출되지 않으므로 직접 타이머를 시작한다.
        self.wait_start_time = get_time()

        # IDLE --time_out--> SLEEP --space_down--> IDLE
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP'],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,  # IDLE 에서 SPACE 를 눌러도 무시
        )

    # IDLE 로 돌아올 때마다 5초 타이머를 다시 시작한다.
    def on_enter_IDLE(self):
        self.wait_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.space_down()

    def update(self):
        now = get_time()
        dt = now - self.last_time
        self.last_time = now

        # SLEEP 이면 누운 쪽(1.0)으로, IDLE 이면 선 쪽(0.0)으로 조금씩 움직인다.
        step = dt / LIE_DOWN_TIME
        if self.state == 'SLEEP':
            self.lie = min(1.0, self.lie + step)
        else:
            self.lie = max(0.0, self.lie - step)

        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8  # 자는 동안은 움직이지 않는다.
            if now - self.wait_start_time >= SLEEP_WAIT_TIME:
                self.time_out()

    def draw(self):
        # 제곱을 써서 처음엔 천천히, 끝에선 빠르게 넘어지도록 한다.
        angle = (math.pi / 2) * self.lie * self.lie

        # 발뒤꿈치를 축으로 그림 중심을 회전시킨다. (angle 0 이면 원래 위치)
        c, s = math.cos(angle), math.sin(angle)
        cx = self.x - HEEL_DX + HEEL_DX * c - HEEL_DY * s
        cy = self.y - HEEL_DY + HEEL_DX * s + HEEL_DY * c
        self.image.clip_composite_draw(self.frame * 100, 300, 100, 100, angle, '', cx, cy, 100, 100)
