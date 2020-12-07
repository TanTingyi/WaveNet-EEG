from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import Conv2D, AveragePooling2D
from tensorflow.keras.layers import SeparableConv2D, DepthwiseConv2D
from tensorflow.keras.layers import BatchNormalization, LayerNormalization
from tensorflow.keras.layers import Input, Flatten
from tensorflow.keras.regularizers import l1, l2

from ..layers import SincConv


def SEEGNet(nclass,
            channel_size,
            sample_size,
            sample_rate,
            kernel_size,
            F1,
            min_low_hz=1,
            min_band_hz=1,
            D=1,
            dropout_rate=0.2,
            l1_reg=0.001,
            l2_reg=0.1,
            *args,
            **kwargs):

    inputs = Input(shape=(channel_size, sample_size, 1))
    ##################################################################
    x = SincConv(filters=F1,
                 kernel_size=kernel_size,
                 sample_rate=sample_rate,
                 min_low_hz=min_low_hz,
                 min_band_hz=min_band_hz)(inputs)
    x = BatchNormalization()(x)

    x = DepthwiseConv2D((channel_size, 1),
                        use_bias=False,
                        depth_multiplier=D,
                        depthwise_regularizer=l2(l2_reg))(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dropout(dropout_rate)(x)
    x = Conv2D(F1 * D, 1, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = AveragePooling2D((1, 4))(x)
    x = Dropout(dropout_rate)(x)

    x = DepthwiseConv2D((1, 16), use_bias=False, padding='same')(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Dropout(dropout_rate)(x)
    x = Conv2D(F1 * D, 1, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = AveragePooling2D((1, 8))(x)
    x = Dropout(dropout_rate)(x)

    x = Flatten(name='flatten')(x)
    x = Dense(nclass, name='dense')(x)
    softmax = Activation('softmax', name='softmax')(x)

    return Model(inputs=inputs, outputs=softmax)