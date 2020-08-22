from tflite_runtime.interpreter import Interpreter
import numpy as np
from PIL import Image
from time import time

class ImageClassifier:

    def __init__(self):
        try:
            self.interpreter = Interpreter(model_path='model.tflite')        
            self.interpreter.allocate_tensors()
            _, self.height, self.width, _ = self.interpreter.get_input_details()[0]['shape']
            print('model successfully loaded')
        except Exception as e:
            print("error:", e)
            return

    def get_output_tensor(self, index):
        """Returns the output tensor at the given index."""
        output_details = self.interpreter.get_output_details()[index]
        tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))

        # # If the model is quantized (uint8 data), then dequantize the results
        # if output_details['dtype'] == np.uint8:
        #     scale, zero_point = output_details['quantization']
        #     tensor = scale * (tensor - zero_point)

        return tensor

    def set_input_tensor(self, image):
        tensor_index = self.interpreter.get_input_details()[0]['index']
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def __call__(self, stream, top_k=1):
        # start_time = time()
        image = Image.open(stream).convert('RGB').resize((self.width, self.height), Image.ANTIALIAS)
        image = np.array(image).astype('float') / 255.0

        self.set_input_tensor(image)
        self.interpreter.invoke()

        classes = self.get_output_tensor(1)
        scores = self.get_output_tensor(2)

        # print('classes', classes)
        # print('scores', scores)

        index = np.argmax(scores)
        # elapsed_ms = (time() - start_time) * 1000
        return int(classes[index]), scores[index]
