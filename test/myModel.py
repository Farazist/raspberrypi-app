import tensorflow as tf
import time

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'images/labelmap.pbtxt'

t = time.time()
detection_model = tf.saved_model.load('test/saved_model')
print('model loaded 1')
model_fn = detection_model.signatures['serving_default']
print('model loaded 2')
print(time.time() - t)
