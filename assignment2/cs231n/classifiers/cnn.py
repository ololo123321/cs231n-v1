import numpy as np

from cs231n.layers import *
from cs231n.fast_layers import *
from cs231n.layer_utils import *


class ThreeLayerConvNet:
    """
    A three-layer convolutional network with the following architecture:

    conv - relu - 2x2 max pool - affine - relu - affine - softmax

    The network operates on minibatches of data that have shape (N, C, H, W)
    consisting of N images, each with height H and width W and with C input
    channels.
    """

    def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
                 hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
                 dtype=np.float32):
        """
        Initialize a new network.

        Inputs:
        - input_dim: Tuple (C, H, W) giving size of input data
        - num_filters: Number of filters to use in the convolutional layer
        - filter_size: Width/height of filters to use in the convolutional layer
        - hidden_dim: Number of units to use in the fully-connected hidden layer
        - num_classes: Number of scores to produce from the final affine layer.
        - weight_scale: Scalar giving standard deviation for random initialization
          of weights.
        - reg: Scalar giving L2 regularization strength
        - dtype: numpy datatype to use for computation.
        """
        self.params = {}
        self.reg = reg
        self.dtype = dtype

        ############################################################################
        # TODO: Initialize weights and biases for the three-layer convolutional    #
        # network. Weights should be initialized from a Gaussian centered at 0.0   #
        # with standard deviation equal to weight_scale; biases should be          #
        # initialized to zero. All weights and biases should be stored in the      #
        #  dictionary self.params. Store weights and biases for the convolutional  #
        # layer using the keys 'W1' and 'b1'; use keys 'W2' and 'b2' for the       #
        # weights and biases of the hidden affine layer, and keys 'W3' and 'b3'    #
        # for the weights and biases of the output affine layer.                   #
        #                                                                          #
        # IMPORTANT: For this assignment, you can assume that the padding          #
        # and stride of the first convolutional layer are chosen so that           #
        # **the width and height of the input are preserved**. Take a look at      #
        # the start of the loss() function to see how that happens.                #                           
        ############################################################################
        h = input_dim[1]
        for i in range(3):
            if i == 0:
                self.params['W1'] = np.random.randn(num_filters, 3, filter_size, filter_size) * weight_scale
                self.params['b1'] = np.zeros(num_filters)
            elif i == 1:
                self.params['W2'] = np.random.randn(num_filters * (h // 2)**2, hidden_dim) * weight_scale
                self.params['b2'] = np.zeros(hidden_dim)
            else:
                self.params['W3'] = np.random.randn(hidden_dim, num_classes) * weight_scale
                self.params['b3'] = np.zeros(num_classes)

        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """
        Evaluate loss and gradient for the three-layer convolutional network.

        Input / output: Same API as TwoLayerNet in fc_net.py.
        """
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        W3, b3 = self.params['W3'], self.params['b3']

        filter_size = W1.shape[2]
        conv_param = {'stride': 1, 'pad': (filter_size - 1) // 2}
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

        N = X.shape[0]
        out_conv, cache1 = conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)
        out, cache2 = affine_relu_forward(out_conv.reshape(N, -1), W2, b2)
        scores, cache3 = affine_forward(out, W3, b3)

        if y is None:
            return scores

        loss, dx = softmax_loss(scores, y)
        for name, param in self.params.items():
            if 'W' in name:
                loss += 0.5 * self.reg * np.sum(param * param)

        grads = {}
        dx, dw, db = affine_backward(dx, cache3)
        grads['W3'] = dw
        grads['b3'] = db
        dx, dw, db = affine_relu_backward(dx, cache2)
        grads['W2'] = dw
        grads['b2'] = db
        dx, dw, db = conv_relu_pool_backward(dx.reshape(*out_conv.shape), cache1)
        grads['W1'] = dw
        grads['b1'] = db

        return loss, grads