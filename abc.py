import kivy
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label

import cv2
from detection.objectDetection import Detect
import pyttsx3

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        self.detector = Detect()  # Instantiate your object detection class
        self.engine = pyttsx3.init()  # Initialize text-to-speech engine
        Clock.schedule_interval(self.update, 1.0 / fps)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Perform object detection
            people = self.detector.run(frame)

            # Say the detected object using text-to-speech engine
            if people:
                self.engine.say(people[0])
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

class CamApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=30)
        return self.my_camera

    def on_stop(self):
        # Without this, app will not exit even if the window is closed
        self.capture.release()

if __name__ == '__main__':
    CamApp().run()

