import kivy
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Point, GraphicException
from kivy.metrics import dp
from random import random
from math import sqrt
import time

import cv2
from detection.objectDetection import Detect
import pyttsx3

class KivyCamera(Image):
    def __init__(self, capture, fps, resolution=(2048, 1080), **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        self.detector = Detect()  # Instantiate your object detection class
        self.engine = pyttsx3.init()  # Initialize text-to-speech engine
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Perform object detection
            people = self.detector.run(frame)

            # Say the detected object using text-to-speech engine
            if people:
                # self.engine.say(people[0])
                self.engine.runAndWait()
                print(people)

            # Convert frame to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Display image from the texture
            self.texture = image_texture

class TouchCamera(BoxLayout):
    def __init__(self, **kwargs):
        super(TouchCamera, self).__init__(**kwargs)
        self.det = Detect()
        self.engine = pyttsx3.init()

    def normalize_pressure(self, pressure):
        if pressure == 0.0:
            return 1
        return dp(pressure * 10)

    def on_touch_down(self, touch):
        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 5
        if 'pressure' in touch.profile:
            ud['pressure'] = touch.pressure
            pointsize = self.normalize_pressure(touch.pressure)
        ud['color'] = random()

        with self.canvas:
            Color(ud['color'], 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y),
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        self.update_touch_label(ud['label'], touch)
        self.add_widget(ud['label'])
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        ud = touch.ud
        ud['lines'][0].pos = touch.x, 0
        ud['lines'][1].pos = 0, touch.y

        index = -1

        while True:
            try:
                points = ud['lines'][index].points
                oldx, oldy = points[-2], points[-1]
                break
            except IndexError:
                index -= 1

        points = self.calculate_points(oldx, oldy, touch.x, touch.y)

        if 'pressure' in ud:
            old_pressure = ud['pressure']
            if (
                not old_pressure
                or not .99 < (touch.pressure / old_pressure) < 1.01
            ):
                g = ud['group']
                pointsize = self.normalize_pressure(touch.pressure)
                with self.canvas:
                    Color(ud['color'], 1, 1, mode='hsv', group=g)
                    ud['lines'].append(
                        Point(points=(), pointsize=pointsize, group=g))

        if points:
            try:
                lp = ud['lines'][-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass

        ud['label'].pos = touch.pos
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        self.update_touch_label(ud['label'], touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        ud = touch.ud
        self.canvas.remove_group(ud['group'])
        self.remove_widget(ud['label'])

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20

    def calculate_points(self, x1, y1, x2, y2, steps=5):
        dx = x2 - x1
        dy = y2 - y1
        dist = sqrt(dx * dx + dy * dy)
        if dist < steps:
            return
        o = []
        m = dist / steps
        for i in range(1, int(m)):
            mi = i / m
            lastx = x1 + dx * mi
            lasty = y1 + dy * mi
            o.extend([lastx, lasty])
        return o

class TestCamera(App):

    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.capture = cv2.VideoCapture(0)
        self.kivy_camera = KivyCamera(capture=self.capture, fps=60, resolution=(2048, 1080))
        self.touch_camera = TouchCamera()
        layout.add_widget(self.kivy_camera)
        layout.add_widget(self.touch_camera)
        return layout

    def on_stop(self):
        # Without this, app will not exit even if the window is closed
        self.capture.release()

if __name__ == '__main__':
    TestCamera().run()

