"""Boy 상태 머신 자동 테스트.

창을 띄우지 않고, 시계(get_time)를 가짜로 바꿔서 상태 전이와 이동을 확인한다.
실행: python test_boy.py
"""
import os
import sys
import types
import unittest

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

import boy as boy_module
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_a

CANVAS_WIDTH = 800


def key(event_type, k):
    return types.SimpleNamespace(type=event_type, key=k)


class BoyTestCase(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        boy_module.get_time = lambda: self.now
        boy_module.load_image = lambda name: None
        boy_module.get_canvas_width = lambda: CANVAS_WIDTH
        self.boy = boy_module.Boy()

    def step(self, t):
        """시계를 t 초로 옮기고 update 한 번."""
        self.now = t
        self.boy.update()

    def run_until(self, t, dt=0.01):
        """dt 간격으로 t 초까지 update. 마지막 걸음은 정확히 t 에 맞춘다."""
        while self.now < t:
            self.step(min(t, self.now + dt))

    def press(self, k):
        self.boy.handle_event(key(SDL_KEYDOWN, k))

    def release(self, k):
        self.boy.handle_event(key(SDL_KEYUP, k))


class TestIdleSleep(BoyTestCase):
    def test_idle_to_sleep_after_5_seconds(self):
        self.step(4.99)
        self.assertEqual(self.boy.state, 'IDLE')
        self.step(5.0)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_space_wakes_up_and_restarts_timer(self):
        self.step(5.0)
        self.press(SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.wait_start_time, 5.0)
        self.step(9.99)
        self.assertEqual(self.boy.state, 'IDLE')
        self.step(10.0)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_space_in_idle_is_ignored(self):
        self.press(SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_lies_down_slowly(self):
        self.step(5.0)
        self.step(5.3)
        self.assertTrue(0.0 < self.boy.lie < 1.0)
        self.run_until(6.0)
        self.assertEqual(self.boy.lie, 1.0)


class TestRun(BoyTestCase):
    def test_arrow_runs_and_release_stops(self):
        self.press(SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.step(0.5)
        self.assertEqual(self.boy.face_dir, 1)
        self.assertAlmostEqual(self.boy.x, 400 + 150)
        self.release(SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_both_arrows_stand_and_one_release_keeps_running(self):
        self.press(SDLK_RIGHT)
        self.press(SDLK_LEFT)
        self.assertEqual(self.boy.state, 'IDLE')
        self.release(SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.step(0.1)
        self.assertEqual(self.boy.face_dir, -1)

    def test_run_stays_inside_canvas(self):
        self.press(SDLK_RIGHT)
        self.run_until(3.0)
        self.assertEqual(self.boy.x, CANVAS_WIDTH - boy_module.HALF_WIDTH)
        self.release(SDLK_RIGHT)
        self.press(SDLK_LEFT)
        self.run_until(6.0)
        self.assertEqual(self.boy.x, boy_module.HALF_WIDTH)

    def test_arrow_in_sleep_gets_up_quickly_then_runs(self):
        self.run_until(6.0)  # 5초에 잠들고 다 누움
        self.assertEqual(self.boy.lie, 1.0)
        self.press(SDLK_RIGHT)
        self.assertEqual(self.boy.state, 'RUN')
        self.step(6.1)  # 일어나는 중에는 제자리
        self.assertTrue(0.0 < self.boy.lie < 1.0)
        self.assertEqual(self.boy.x, 400)
        self.run_until(6.3)  # 0.2초면 다 일어나 달리기 시작
        self.assertEqual(self.boy.lie, 0.0)
        self.assertGreater(self.boy.x, 400)


class TestAutoRun(BoyTestCase):
    # 채점: 'a' 누르면 auto run 상태 이동
    def test_a_key_starts_auto_run_without_arrow_keys(self):
        self.press(SDLK_a)
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.assertIsInstance(self.boy.machine.get_state('AUTO_RUN'), boy_module.AutoRun)
        self.step(0.3)
        self.assertGreater(self.boy.x, 400)  # 키를 안 눌러도 계속 움직인다.

    def test_a_key_only_from_idle(self):
        self.press(SDLK_RIGHT)
        self.press(SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.release(SDLK_RIGHT)
        self.run_until(5.0)
        self.press(SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')

    # 채점: 5초 이상 경과하면 Idle 상태 복귀
    def test_back_to_idle_after_5_seconds(self):
        self.step(2.0)
        self.press(SDLK_a)
        self.run_until(6.99)
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.run_until(7.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.wait_start_time, 7.0)  # IDLE 의 수면 타이머 재시작

    # 채점: 속도가 빨라지고 크기가 커짐
    def test_faster_and_bigger(self):
        self.press(SDLK_a)
        self.assertEqual(self.boy.scale, boy_module.AUTO_RUN_SCALE)
        self.assertGreater(boy_module.AUTO_RUN_SCALE, 1.0)
        self.step(0.5)
        self.assertAlmostEqual(self.boy.x, 400 + boy_module.AUTO_RUN_SPEED * 0.5)
        self.assertGreater(boy_module.AUTO_RUN_SPEED, boy_module.RUN_SPEED)

    def test_size_back_to_normal_after_auto_run(self):
        self.press(SDLK_a)
        self.run_until(5.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.scale, 1.0)

    # 채점: 좌우측 끝에서 자동 방향 전환
    def test_turns_around_at_both_edges(self):
        self.press(SDLK_a)
        half = boy_module.HALF_WIDTH * boy_module.AUTO_RUN_SCALE
        turns = []
        while self.now < 3.0:
            before = self.boy.face_dir
            self.step(self.now + 0.01)
            self.assertTrue(half <= self.boy.x <= CANVAS_WIDTH - half)  # 커진 몸도 화면 안
            if self.boy.face_dir != before:
                turns.append((self.boy.x, self.boy.face_dir))
        self.assertEqual(turns[:3], [(CANVAS_WIDTH - half, -1), (half, 1), (CANVAS_WIDTH - half, -1)])

    # 방향키가 눌리면 무적 런 취소, 누른 방향으로 원래 RUN
    def test_arrow_cancels_auto_run(self):
        self.press(SDLK_a)
        self.step(0.2)
        x = self.boy.x
        self.press(SDLK_LEFT)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.scale, 1.0)
        self.step(0.3)
        self.assertEqual(self.boy.face_dir, -1)
        self.assertAlmostEqual(self.boy.x, x - boy_module.RUN_SPEED * 0.1)
        self.run_until(6.0)
        self.assertEqual(self.boy.state, 'RUN')  # 무적 런의 5초 타이머는 더 이상 상관없다.

    def test_space_in_auto_run_is_ignored(self):
        self.press(SDLK_a)
        self.press(SDLK_SPACE)
        self.assertEqual(self.boy.state, 'AUTO_RUN')


if __name__ == '__main__':
    unittest.main(verbosity=2)
