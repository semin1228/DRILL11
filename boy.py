from pico2d import load_image, get_time, SDL_KEYDOWN, SDLK_SPACE
from transitions import Machine

SLEEP_WAIT_TIME = 5.0  # IDLE 상태로 이 시간(초)이 지나면 SLEEP 으로 간다.


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.image = load_image('animation_sheet.png')

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
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE' and get_time() - self.wait_start_time >= SLEEP_WAIT_TIME:
            self.time_out()

    def draw(self):
        if self.state == 'IDLE':
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # IDLE 이미지를 90도 회전시켜 누운 모습으로 그린다.
            self.image.clip_composite_draw(self.frame * 100, 300, 100, 100,
                                           3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
