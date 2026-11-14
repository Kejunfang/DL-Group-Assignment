"""BiT-M R50x1 (pre-activation ResNet-50 with GroupNorm + weight-standardised convs) in Keras 3,
plus loading of the timm/Google weights (resnetv2_50x1_bit.goog_in21k)."""
import keras
from keras import ops


class StdConv2D(keras.layers.Conv2D):
    # Convolution whose kernel is standardised (zero mean, unit variance per output filter) before use
    def call(self, inputs):
        k = self.kernel
        mean = ops.mean(k, axis=(0, 1, 2), keepdims=True)
        var = ops.var(k, axis=(0, 1, 2), keepdims=True)
        return self.convolution_op(inputs, (k - mean) / ops.sqrt(var + 1e-8))


def conv(x, filters, size, stride, name):
    pad = ((stride - 1) + (size - 1)) // 2
    if pad:
        x = keras.layers.ZeroPadding2D(pad, name=name + "_pad")(x)
    return StdConv2D(filters, size, strides=stride, use_bias=False, name=name)(x)


def gn_relu(x, name):
    x = keras.layers.GroupNormalization(groups=32, epsilon=1e-5, name=name)(x)
    return keras.layers.ReLU(name=name + "_relu")(x)


def build_bit_r50(input_shape):
    inputs = keras.Input(input_shape)
    x = conv(inputs, 64, 7, 2, "stem_conv")
    x = keras.layers.ZeroPadding2D(1, name="stem_pool_pad")(x)
    x = keras.layers.MaxPooling2D(3, 2, name="stem_pool")(x)
    for s, (blocks, width) in enumerate(zip([3, 4, 6, 3], [64, 128, 256, 512])):
        for b in range(blocks):
            n = f"stages_{s}_blocks_{b}"
            stride = 2 if (b == 0 and s > 0) else 1
            pre = gn_relu(x, n + "_norm1")
            shortcut = conv(pre, width * 4, 1, stride, n + "_downsample_conv") if b == 0 else x
            y = conv(pre, width, 1, 1, n + "_conv1")
            y = conv(gn_relu(y, n + "_norm2"), width, 3, stride, n + "_conv2")
            y = conv(gn_relu(y, n + "_norm3"), width * 4, 1, 1, n + "_conv3")
            x = keras.layers.Add(name=n + "_add")([y, shortcut])
    x = gn_relu(x, "norm")
    return keras.Model(inputs, x, name="bit_m_r50x1")


def load_timm_weights(model, weights):
    # weights: dict name -> numpy array in PyTorch layout
    used = set()
    for layer in model.layers:
        key = layer.name.replace("_blocks_", ".blocks.").replace("stages_", "stages.")
        key = key.replace("stem_conv", "stem.conv").replace("_downsample_conv", ".downsample.conv")
        key = key.replace("_conv", ".conv").replace("_norm", ".norm")
        if isinstance(layer, StdConv2D):
            layer.set_weights([weights[key + ".weight"].transpose(2, 3, 1, 0)])
            used.add(key + ".weight")
        elif isinstance(layer, keras.layers.GroupNormalization):
            layer.set_weights([weights[key + ".weight"], weights[key + ".bias"]])
            used |= {key + ".weight", key + ".bias"}
    missing = set(weights) - used - {"head.fc.weight", "head.fc.bias"}
    assert not missing, sorted(missing)[:5]
