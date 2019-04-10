from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import matplotlib.pyplot as plt, mpld3

from django.views import generic

class IndexView(generic.TemplateView):
    template_name = 'ml/index.html'

def train_model(request):
    # https://www.oreilly.com/learning/not-another-mnist-tutorial-with-tensorflow
    import tensorflow as tf

    # import the MNIST data set
    # In our data set, there are 55,000 examples of handwritten digits from zero to nine.
    # Each example is a 28x28 pixel image flattened in an array with 784 values representing each pixel’s intensity.
    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

    # Define our session
    sess = tf.Session()

    # Now, we will define the placeholders x and y_.
    # A placeholder, as the name suggests, is a variable used to feed data into.
    # The only requirement is that in order to feed data into this variable, we need to match its shape and type exactly.

    # Here, we define our x placeholder as the variable to feed our x_train data into.
    # When we assign None to our placeholder, it means the placeholder can be fed as many examples as you want to give it.
    # In this case, our placeholder can be fed any multitude of 784-sized values.
    x = tf.placeholder(tf.float32, shape=[None, 784])

    # We then define y_, which will be used to feed y_train into.
    # This will be used later so we can compare the ground truths to our predictions.
    # We can also think of our labels as classes
    y_ = tf.placeholder(tf.float32, shape=[None, 10])

    # Next, we will define the weights W and bias b.
    # These two values are the grunt workers of the classifier.
    # They will be the only values we will need to calculate our prediction after the classifier is trained.

    # We will first set our weight and bias values to zeros because TensorFlow will optimize these values later.
    # Notice how our W is a collection of 784 values for each of the 10 classes:
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))

    # We will now define y, which is our classifier function.
    # This particular classifier is also known as multinomial logistic regression.
    # We make our prediction by multiplying each flattened digit by our weight and then adding our bias
    y = tf.nn.softmax(tf.matmul(x, W) + b)

    # Next, we will create our cross_entropy function, also known as a loss or cost function.
    # It measures how good (or bad) of a job we are doing at classifying. The higher the cost, the higher the level of inaccuracy.
    # It calculates accuracy by comparing the true values from y_train to the results of our prediction y for each example.
    # The goal is to minimize your loss.
    # This function is taking the log of all our predictions y (whose values range from 0 to 1) and element wise multiplying by the example’s true value y_.
    # If the log function for each value is close to zero, it will make the value a large negative number (i.e., -np.log(0.01) = 4.6).
    # If it is close to 1, it will make the value a small negative number (i.e., -np.log(0.99) = 0.1).
    # We are essentially penalizing the classifier with a very large number if the prediction is confidently incorrect and a very small number if the prediction is confidendently correct.
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

    # Load all the data
    # For x, we have loaded 5,500 examples each with 784 pixels.
    # The y data is the associated labels for all the x_train examples.
    # Rather than storing the label as an integer, it is stored as a 1x10 binary array with the one representing the digit.
    # This is also known as one-hot encoding.
    x_train, y_train = TRAIN_SIZE(mnist, 5500)
    x_test, y_test = TEST_SIZE(mnist, 5500)


    LEARNING_RATE = 0.1
    TRAIN_STEPS = 2500

    # We can now initialize all variables so that they can be used by our TensorFlow graph
    init = tf.global_variables_initializer()
    sess.run(init)

    training = tf.train.GradientDescentOptimizer(LEARNING_RATE).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # Now, we’ll define a loop that repeats TRAIN_STEPS times;
    # For each loop, it runs training, feeding in values from x_train and y_train using feed_dict.
    # In order to calculate accuracy, it will run accuracy to classify the unseen data in x_test by comparing its y and y_test.
    # It is vitally important that our test data was unseen and not used for training data.
    # If a teacher were to give students a practice exam and use that same exam for the final exam, you would have a very biased measure of students’ knowledge
    for i in range(TRAIN_STEPS + 1):
        sess.run(training, feed_dict={x: x_train, y_: y_train})
        if i % 100 == 0:
            print('Training Step:' + str(i) +
                  '  Accuracy = ' + str(sess.run(accuracy, feed_dict={x: x_test, y_: y_test})) +
                  '  Loss = ' + str(sess.run(cross_entropy, {x: x_train, y_: y_train})))

    # for i in range(10):
    #     plt.subplot(2, 5, i + 1)
    #     weight = sess.run(W)[:, i]
    #     plt.title(i)
    #     plt.imshow(weight.reshape([28, 28]), cmap=plt.get_cmap('seismic'))
    #     frame1 = plt.gca()
    #     frame1.axes.get_xaxis().set_visible(False)
    #     frame1.axes.get_yaxis().set_visible(False)
    #
    # plt.show()

    # x_train, y_train = TRAIN_SIZE(1)
    # display_digit(0)
    # answer = sess.run(y, feed_dict={x: x_train})
    # print(answer)
    #
    # answer.argmax()
    return render(request, 'ml/ajax/train_data.html', {"total_training_images_in_dataset": str(mnist.train.images.shape),
                                                       "x_train_Examples_Loaded": str(x_train.shape),
                                                       "y_train_Examples_Loaded": str(y_train.shape),
                                                       "total_test_images_in_dataset": str(mnist.test.images.shape),
                                                       "x_test_Examples_Loaded": str(x_test.shape),
                                                       "y_test_Examples_Loaded": str(y_test.shape)})

def TRAIN_SIZE(mnist, num):
    print ('Total Training Images in Dataset = ' + str(mnist.train.images.shape))
    print ('--------------------------------------------------')
    x_train = mnist.train.images[:num,:]
    print ('x_train Examples Loaded = ' + str(x_train.shape))
    y_train = mnist.train.labels[:num,:]
    print ('y_train Examples Loaded = ' + str(y_train.shape))
    print('')
    return x_train, y_train

def TEST_SIZE(mnist, num):
    print ('Total Test Examples in Dataset = ' + str(mnist.test.images.shape))
    print ('--------------------------------------------------')
    x_test = mnist.test.images[:num,:]
    print ('x_test Examples Loaded = ' + str(x_test.shape))
    y_test = mnist.test.labels[:num,:]
    print ('y_test Examples Loaded = ' + str(y_test.shape))
    return x_test, y_test

def display_digit(x_train, y_train, num):
    print(y_train[num])
    label = y_train[num].argmax(axis=0)
    image = x_train[num].reshape([28,28])
    plt.title('Example: %d  Label: %d' % (num, label))
    plt.imshow(image, cmap=plt.get_cmap('gray_r'))
    mpld3.show(port=8000)

def display_mult_flat(x_train, start, stop):
    images = x_train[start].reshape([1,784])
    for i in range(start+1,stop):
        images = np.concatenate((images, x_train[i].reshape([1,784])))
    plt.imshow(images, cmap=plt.get_cmap('gray_r'))
    mpld3.show(port=8000)

def display_compare(mnist, sess, num):
    # THIS WILL LOAD ONE TRAINING EXAMPLE
    x_train = mnist.train.images[num,:].reshape(1,784)
    y_train = mnist.train.labels[num,:]
    # THIS GETS OUR LABEL AS A INTEGER
    label = y_train.argmax()
    # THIS GETS OUR PREDICTION AS A INTEGER
    prediction = sess.run(y, feed_dict={x: x_train}).argmax()
    plt.title('Prediction: %d Label: %d' % (prediction, label))
    plt.imshow(x_train.reshape([28,28]), cmap=plt.get_cmap('gray_r'))
    plt.show()
