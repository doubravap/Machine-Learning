#Three Layered architecture
#1024 nodes in first layer and 512 in second 256 third
#Xavier Initializer achieves 95.7% accuracy on 6000 iterations otherwise 94.0%
#Decaying Learning Rate
#Dropout with probability 0.5 at all layers
from __future__ import print_function
import numpy as np
import tensorflow as tf
from six.moves import cPickle as pickle
from six.moves import range

pickle_file = 'notMNIST.pickle'

with open(pickle_file, 'rb') as f:
  save = pickle.load(f)
  train_dataset = save['train_dataset']
  train_labels = save['train_labels']
  valid_dataset = save['valid_dataset']
  valid_labels = save['valid_labels']
  test_dataset = save['test_dataset']
  test_labels = save['test_labels']
  print('Training set', train_dataset.shape, train_labels.shape)
  print('Validation set', valid_dataset.shape, valid_labels.shape)
  print('Test set', test_dataset.shape, test_labels.shape)

print("###############REFORMATTING################")
image_size = 28
num_labels = 10

def reformat(dataset, labels):
  dataset = dataset.reshape((-1, image_size * image_size)).astype(np.float32)
  labels = (np.arange(num_labels) == labels[:,None]).astype(np.float32)
  return dataset, labels

train_dataset, train_labels = reformat(train_dataset, train_labels)
valid_dataset, valid_labels = reformat(valid_dataset, valid_labels)
test_dataset, test_labels = reformat(test_dataset, test_labels)
print('Training set', train_dataset.shape, train_labels.shape)
print('Validation set', valid_dataset.shape, valid_labels.shape)
print('Test set', test_dataset.shape, test_labels.shape)

def accuracy(predictions, labels):
  return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1))
          / predictions.shape[0])


###########################MODEL######################
def weight_variable(shape,name):
 # initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.get_variable(name,shape=shape,initializer=tf.contrib.layers.xavier_initializer())

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

batch_size=512
graph=tf.Graph()

with graph.as_default():
  ################VARIABLE LEARNING RATE##############
  global_step=tf.Variable(0)
  starter_learning_rate=0.6
  print(starter_learning_rate)
  decay_steps=200
  print(decay_steps)
  decay_rate=0.70
  print(decay_rate)
  learning_rate=tf.train.exponential_decay(starter_learning_rate,global_step,decay_steps,decay_rate,staircase=True)
  #####################################################

  tf_train_dataset= tf.placeholder(tf.float32,shape=[batch_size,image_size*image_size])
  tf_train_labels= tf.placeholder(tf.float32,shape=[batch_size,num_labels])
  tf_valid_dataset=tf.constant(valid_dataset)
  tf_test_dataset=tf.constant(test_dataset)
  keep_probability=tf.placeholder(tf.float32)
  W1=weight_variable([image_size*image_size,1024],'input')
  W1_1=weight_variable([1024,512],'first') #Second Layer
  W2_1=weight_variable([512,256],'second')
  W2=weight_variable([256,num_labels],'third')

  B1=bias_variable([1024])
  B1_1=bias_variable([512])
  B2_1=bias_variable([256])
  B2=bias_variable([num_labels])
  
  hidden_output=tf.nn.dropout(tf.nn.relu(tf.matmul(tf_train_dataset,W1)+B1),keep_probability) #Layer 1
  hidden_out_2=tf.nn.dropout(tf.nn.relu(tf.matmul(hidden_output,W1_1)+B1_1),keep_probability) #Layer 2
  hidden_out_3=tf.nn.dropout(tf.nn.relu(tf.matmul(hidden_out_2,W2_1)+B2_1),keep_probability)  #Layer 3
  logits=tf.matmul(hidden_out_3,W2)+B2    # Output Layer
  Objective=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=tf_train_labels,logits=logits)) #turning off L2 regularization on weights
  optimizer=tf.train.GradientDescentOptimizer(learning_rate).minimize(Objective)
  train_prediction=tf.nn.reluß(logits)
  test_prediction=tf.nn.relu(tf.matmul(tf.nn.dropout(tf.nn.relu(tf.matmul(tf.nn.dropout(tf.nn.relu(tf.matmul(tf.nn.dropout(tf.nn.relu(tf.matmul(tf_test_dataset,W1)+B1),keep_probability),W1_1)+B1_1),keep_probability),W2_1)+B2_1),keep_probability),W2)+B2)
#########################SESSION#########################M

num_steps = 6001 

with tf.Session(graph=graph) as session:
  tf.global_variables_initializer().run()
  print("Initialized")
  for step in range(num_steps):
    offset = (step * batch_size) % (train_labels.shape[0] - batch_size)
    # Generate a minibatch.
    batch_data = train_dataset[offset:(offset + batch_size), :]
    batch_labels = train_labels[offset:(offset + batch_size), :]
    feed_dict = {tf_train_dataset : batch_data, tf_train_labels : batch_labels, keep_probability: 0.5}
    _, l, predictions = session.run([optimizer, Objective, train_prediction], feed_dict=feed_dict)
    if (step % 500 == 0):
      print("Minibatch loss at step %d: %f" % (step, l))
      print("Minibatch accuracy: %.1f%%" % accuracy(predictions, batch_labels))
  feed_dict[keep_probability]= 1.0;
  print("Test accuracy: %.1f%%" % accuracy(test_prediction.eval(feed_dict), test_labels))

