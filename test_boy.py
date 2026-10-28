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
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT

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
        """dt 간격으로 t 초까지 update."""
        while self.now < t - 1e-9:
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
