

from cgi import test
import kivy
import kivymd
import cv2


from camera import doorBellApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from imutils.video import FPS


notify = {'No records':'',}

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 0.0001 / fps)
        self.codec = cv2.VideoWriter_fourcc(*'XVID')
        self.output = cv2.VideoWriter('CAPTURE.avi', self.codec, 30, (640, 480))
        self.rec = None

    def update(self, *args):
        fps = FPS().start()
        self.frame = self.capture.read()[1]               
        if self.frame is not None:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (1,1), 0)
            _, thresh = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY)
            erode = cv2.erode(thresh, None, iterations=10)
            dilated = cv2.dilate(erode, None, iterations=10)
            contours, hier = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours != ():
                c = max(contours, key = cv2.contourArea)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(self.frame, (x, y), (x+h, y+w), (255, 0, 255), 2)
                cv2.putText(self.frame, "Status: {}".format('Movement'), (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3) 
            buf1 = cv2.flip(self.frame, 0)
            buf = buf1.tobytes()
            image_texture = Texture.create(
                size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = image_texture
            fps.update()
            if self.rec==True:
                self.output.write(self.frame)
            elif self.rec==False:
                self.output.release()
                self.rec = None

    def pic(self):
        print('picture taken kivycam')
        return cv2.imshow('capture', self.capture.read()[1])

    def recordStr(self):
        #cv2.VideoWriter
        return 'recording.....'

    def recordEnd(self):
        return 'recording ended'
    
    def destroy(self):
        cv2.destroyAllWindows()

    def release(self):
        self.capture.release()

class MainWindow(MDScreen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.widget_level = MDBoxLayout(orientation = 'horizontal')
        self.refresh = MDRectangleFlatButton(text = "Refresh"
                                                , on_release = self.restart_vid
                                                )
        self.capture = cv2.VideoCapture(0) #cv2.VideoCapture('http://10.0.0.178:5000/video_feed')
        self.cam = KivyCamera(capture=self.capture, fps=120)
        self.record = MDRectangleFlatButton(text = "Record"
                                                  , on_release = self.start_record
                                                  )
        self.end_record = MDRectangleFlatButton(text = "End Recording"
                                                , on_release = self.stop_record
                                                )
        self.widget_level.add_widget(self.refresh)
        self.add_widget(self.cam)
        self.widget_level.add_widget(self.record)
        self.widget_level.add_widget(self.end_record)
        self.add_widget(self.widget_level)
        
    def restart_vid(self, *args):
        self.remove_widget(self.cam)
        self.add_widget(self.cam)
        
    def start_record(self, *args):
        self.cam.rec = True
    
    def stop_record(self, *args):
        # print('pressed')
        self.cam.rec = False


class WindowManager(ScreenManager):
    pass

class CamApp(MDApp):
    
    def build(self):
        self.load_kv("chyme.kv")


if __name__ == '__main__':
    CamApp().run()