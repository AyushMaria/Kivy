# from kivy.app import App
# from kivy.uix.image import Image
# from kivy.clock import Clock
# from kivy.graphics.texture import Texture
# from detection.objectDetection import Detect
# import cv2
#
#
# class KivyCamera(Image):
#     personDetect = Detect()
#     def __init__(self, capture, fps, **kwargs):
#         super(KivyCamera, self).__init__(**kwargs)
#         self.capture = capture
#         Clock.schedule_interval(self.update, 1.0 / fps)
#
#
#     def update(self, dt):
#         ret, frame = self.capture.read()
#         if ret:
#             # convert it to texture
#             found, frame = self.personDetect.run(frame)
#             print(found)
#             buf1 = cv2.flip(frame, 0)
#             buf = buf1.tostring()
#             image_texture = Texture.create(
#                 size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
#             image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
#             # display image from the texture
#             self.texture = image_texture
#
#
# class CamApp(App):
#     def build(self):
#         self.capture = cv2.VideoCapture(0)
#         self.my_camera = KivyCamera(capture=self.capture, fps=30)
#         return self.my_camera
#
#
#     def on_stop(self):
#         #without this, app will not exit even if the window is closed
#         self.capture.release()
#
#
# if __name__ == '__main__':
#     CamApp().run()


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.camera import Camera

class MainApp(App):
    def build(self):
        return Camera(play=True, index=1, resolution=(640,480))

if __name__== "__main__":
    MainApp().run()
