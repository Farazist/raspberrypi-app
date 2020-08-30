import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter(model_path='test/model.tflite')        
interpreter.allocate_tensors()
print('model loaded')