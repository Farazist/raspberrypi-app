from io import BytesIO
from tflite_runtime.interpreter import Interpreter
import numpy as np
from PIL import Image
from time import time
import picamera
import matplotlib.pyplot as plt
from IPython.display import display

def get_output_tensor(index):
    """Returns the output tensor at the given index."""
    output_details = interpreter.get_output_details()[index]
    tensor = np.squeeze(interpreter.get_tensor(output_details['index']))

    # # If the model is quantized (uint8 data), then dequantize the results
    # if output_details['dtype'] == np.uint8:
    #     scale, zero_point = output_details['quantization']
    #     tensor = scale * (tensor - zero_point)

    return tensor

def set_input_tensor(image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


interpreter = Interpreter(model_path='model.tflite')        
interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']

with picamera.PiCamera(resolution=(1280, 720), framerate=30) as camera:
    stream = BytesIO()
    camera.start_preview()
    start_time = time()
    for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):

        stream.seek(0)

        image = Image.open(stream).convert('RGB').resize((width, height), Image.ANTIALIAS)
  
        image = np.array(image).astype('float') / 255.0
       
        set_input_tensor(image)
        interpreter.invoke()

        classes = get_output_tensor(1)
        scores = get_output_tensor(2)

        # print('classes', classes)
        # print('scores', scores)

        index = np.argmax(scores)
        elapsed_ms = (time() - start_time)

        label, score = int(classes[index]), scores[index]
        if score > 0.7:
            print(label, score, elapsed_ms)
        stream.seek(0)
        stream.truncate()
