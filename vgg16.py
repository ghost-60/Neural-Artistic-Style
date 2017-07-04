# convnet style transfer using vgg16

from __future__ import print_function

import time
from PIL import Image
import tensorflow as tf
import numpy as np
import sys

from keras import backend
from keras.models import Model
from keras.applications.vgg16 import VGG16
import h5py as hypy
from scipy.optimize import fmin_l_bfgs_b
from scipy.misc import imsave



content_weight = 0.025
style_weight = 5.0
total_variation_weight = 1.0
loss = backend.variable(0.)
height = 512
width = 512


def main():

	global loss

	
	content_image = Image.open(sys.argv[1])
	content_image = content_image.resize((height, width))

	style_image = Image.open(sys.argv[2])
	style_image = style_image.resize((height, width))

	content_array = np.asarray(content_image, dtype='float32')
	content_array = np.expand_dims(content_array, axis=0)
	print("content image loaded in array")
    
	style_array = np.asarray(style_image, dtype='float32')
	style_array = np.expand_dims(style_array, axis=0)
	print("style image loaded in array")
	
	content_array[:, :, :, 0] -= 103.939
	content_array[:, :, :, 1] -= 116.779
	content_array[:, :, :, 2] -= 123.68
	content_array = content_array[:, :, :, ::-1]

	style_array[:, :, :, 0] -= 103.939
	style_array[:, :, :, 1] -= 116.779
	style_array[:, :, :, 2] -= 123.68
	style_array = style_array[:, :, :, ::-1]
	
	content_image = backend.variable(content_array)
	style_image = backend.variable(style_array)
	combination_image = backend.placeholder((1, height, width, 3))
	input_tensor = backend.concatenate([content_image,style_image,
				            combination_image], axis=0)
				            
	# pretrained model
	model = VGG16(input_tensor=input_tensor, weights='imagenet', include_top=False)
	  
	layers = dict([(layer.name, layer.output) for layer in model.layers])
	
	# for content loss
	layer_features = layers['block4_conv2']
	content_image_features = layer_features[0, :, :, :]
	combination_features = layer_features[2, :, :, :]

	loss += content_weight * content_loss(content_image_features,
				              combination_features)
    
    # for style loss				              
	feature_layers = ['block1_conv2', 'block2_conv2', 'block3_conv3','block4_conv3','block5_conv3']
	
	for layer_name in feature_layers:
		layer_features = layers[layer_name]
		style_features = layer_features[1, :, :, :]
		combination_features = layer_features[2, :, :, :]
		sl = style_loss(style_features, combination_features)
		loss += (style_weight / len(feature_layers)) * sl
		
		

	loss += total_variation_weight * total_variation_loss(combination_image)
	grads = backend.gradients(loss, combination_image)
	outputs = [loss]
	outputs += grads
	global f_outputs
	f_outputs = backend.function([combination_image], outputs)
	
	
	evaluator = Evaluator()
	x = np.random.uniform(0, 255, (1, height, width, 3)) - 128.

	iterations = 10

	for i in range(iterations):
		print('Start of iteration', i)
		start_time = time.time()
		x, min_val, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(),
				             fprime=evaluator.grads, maxfun=20)
		print('Current loss value:', min_val)
		end_time = time.time()
		print('Iteration %d completed in %ds' % (i, end_time - start_time))
				             
	x = x.reshape((height, width, 3))
	x = x[:, :, ::-1]
	x[:, :, 0] += 103.939
	x[:, :, 1] += 116.779
	x[:, :, 2] += 123.68
	x = np.clip(x, 0, 255).astype('uint8')

	output=Image.fromarray(x)
	output.show()
	output.save("./images_transfered/transferedblock4.jpg")

		              
	
	
	
def content_loss(content, combination):
	return backend.sum(backend.square(combination - content))

def gram_matrix(x):
	features = backend.batch_flatten(backend.permute_dimensions(x, (2, 0, 1)))
	gram = backend.dot(features, backend.transpose(features))
	return gram
	
def style_loss(style, combination):
	S = gram_matrix(style)
	C = gram_matrix(combination)
	channels = 3
	size = height * width
	return backend.sum(backend.square(S - C)) / (4. * (channels ** 2) * (size ** 2))


def total_variation_loss(x):
	a = backend.square(x[:, :height-1, :width-1, :] - x[:, 1:, :width-1, :])
	b = backend.square(x[:, :height-1, :width-1, :] - x[:, :height-1, 1:, :])
	return backend.sum(backend.pow(a + b, 1.25))


def eval_loss_and_grads(x):
	x = x.reshape((1, height, width, 3))
	outs = f_outputs([x])
	loss_value = outs[0]
	grad_values = outs[1].flatten().astype('float64')
	return loss_value, grad_values

class Evaluator(object):

	def __init__(self):
		self.loss_value = None
		self.grads_values = None

	def loss(self, x):
		assert self.loss_value is None
		loss_value, grad_values = eval_loss_and_grads(x)
		self.loss_value = loss_value
		self.grad_values = grad_values

		return self.loss_value

	def grads(self, x):
		assert self.loss_value is not None
		grad_values = np.copy(self.grad_values)
		self.loss_value = None
		self.grad_values = None
		return grad_values


if __name__== "__main__":
	main()
