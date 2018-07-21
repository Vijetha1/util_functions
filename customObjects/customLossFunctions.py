import os
os.environ['PYTHONHASHSEED'] = '0'
import numpy as np
np.random.seed(42)
import random as rn
rn.seed(12345)
import tensorflow as tf
session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
import keras.backend as K
tf.set_random_seed(1234)
sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
K.set_session(sess)

import keras
import pdb

def catCrossEntr(l1=1):
	def loss(y_true, y_pred):
		classProb = y_pred
		return l1*K.categorical_crossentropy(y_true, classProb)
	return loss


def quantizationLoss(l2=0.01, nbits = 12.0):
	def loss(y_true, y_pred):
		activs = y_pred
		curLoss = -(1./float(nbits))*l2*(K.sum((K.square(activs - 0.5)), axis=1))
		return curLoss
	return loss

def equiProbBits(l3=1):
	def loss(y_true, y_pred):
		activs = y_pred
		curLoss = l3*K.square(K.abs(K.mean(activs, axis =1)-0.5))
		return curLoss
	return loss


def dahLoss():
	def loss(y_true, y_pred):
		epsilon = 0.000001
		D = y_pred - epsilon
		S = y_true
		beta = 0.9
		#curLoss = S - (1 - D)
		curLoss = -1*beta*S*K.log(D) - (1-beta)*(1-S)*K.log(1-D)
		#curLoss = K.binary_crossentropy(S, D)
		return curLoss
	return loss


def contrastive(l2 = 1.0, m = 3.0):
	def loss(y_true, y_pred):
		#S = 1.0 - y_true
		S = y_true
		D = y_pred
		total = K.sum(K.sum(y_true)) + K.sum(K.sum(1.0-y_true))
		beta = K.sum(K.sum(y_true))/total
		#pdb.set_trace()
		#print(beta)
		curLoss = l2*(S*(1.0-beta)*K.square(D) + (1.0-S)*beta*K.square(K.maximum(0.0, m - D)))
		return curLoss
	return loss

def dummy(l2 = 1.0):
	def loss(y_true, y_pred):
		#S = 1.0 - y_true
		TrueDist = 1.0 - y_true
		D = y_pred
		return K.mean(K.square(TrueDist - D), axis=-1)
		# m = 3.0
		# beta = 0.1#0.455078125#K.sum(K.sum(y_true))/1024.
		# #pdb.set_trace()
		# #print(beta)
		# curLoss = l2*(S*(1-beta)*K.square(D) + (1-S)*beta*K.square(K.maximum(0, m - D)))
		# return curLoss
	return loss


def dahLossDummy(y_true, y_pred):
	epsilon = 0.000001
	D = y_pred - epsilon
	S = y_true
	beta = 0.5
	#curLoss = S - (1 - D)
	#curLoss = -1*beta*K.dot(S,K.log(D)) - (1-beta)*K.dot((1-S),K.log(1-D))
	curLoss = K.binary_crossentropy(S, D)
	return curLoss

def vectorLoss(l2=1.0, m = 0.25, batch_size=50):
	def loss(y_true, y_pred):
		multiplier = K.ones((batch_size, batch_size))-K.eye(batch_size)
		#pdb.set_trace()
		multiplier = K.expand_dims(multiplier, axis=0)
		multiplier = K.repeat_elements(multiplier, batch_size, 0)
		curLoss = K.maximum((m - y_pred)*multiplier, 0.)
		return l2*curLoss
	return loss