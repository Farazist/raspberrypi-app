import tflite_runtime.interpreter as tflite
import numpy as np
import cv2 as cv

class ImageClassifier:

    def __init__(self):
        self.interpreter = tflite.Interpreter(model_path='model.tflite')
        print('model successfully loaded')
        self.interpreter.allocate_tensors()
        _, self.height, self.width, _ = self.interpreter.get_input_details()[0]['shape']
        self.output_details = self.interpreter.get_output_details()

    def set_input_tensor(self, interpreter, image):
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def preprocess(self, image):
        image = cv.resize(image, (224, 224))
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = image / 255.0
        return image

    def predict(self, image):
        image = self.preprocess(image)
        self.set_input_tensor(self.interpreter, image)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        print(output_data)