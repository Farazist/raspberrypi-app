import tflite_runtime.interpreter as tflite
import numpy as np
from scipy import stats
from PIL import Image
from time import time

class ImageClassifier:

    def __init__(self):
        try:
            self.interpreter = tflite.Interpreter(model_path='model.tflite')        
            self.interpreter.allocate_tensors()
            _, self.height, self.width, _ = self.interpreter.get_input_details()[0]['shape']
            self.output_details = self.interpreter.get_output_details()[0]
            self.labels = self.load_labels('labels.txt')
            print('model successfully loaded')

        except Exception as e:
            print("error:", e)
            return

    def load_labels(self, path):
        with open(path, 'r') as f:
            return {i: line.strip() for i, line in enumerate(f.readlines())}

    def set_input_tensor(self, interpreter, image):
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def __call__(self, stream):
        start_time = time()

        image = Image.open(stream).convert('RGB').resize((self.width, self.height), Image.ANTIALIAS)
        self.set_input_tensor(self.interpreter, image)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details['index'])

        elapsed_ms = (time() - start_time) * 1000

        # label_id, prob = results[0]
        print(output_data)
        return output_data