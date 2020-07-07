# Author: Allen Wang
# Date: 2020-07-03 14:31 Friday
# File: ~/Projects/sunspot/src/model/sunspot_inception.py
# Description: SunSpot fine tuning

import sys, os
import datetime
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))

import tensorflow as tf
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout

from data_factory import (
    ds, dstep, validation_ds, vstep,
    validation_all_ds, all_data_ds, all_data_step
)


# Multi-GPU single Hosts settings
strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

# Tensorboard
log_dir="/home/ps/Projects/sunspot/logs/fit/" + datetime.datetime.now(
).strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(
    log_dir=log_dir, histogram_freq=1)

base_model = InceptionV3(
    include_top=False,
    weights="imagenet"
    )

x = base_model.output
x = GlobalAveragePooling2D()(x)
# let's add a fully-connected layer
x = Dense(1024, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(3, activation='softmax')(x)


model = Model(inputs=base_model.input, outputs=predictions)

for layer in base_model.layers:
    layer.trainable = False
# with strategy.scope():
model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy'])

model.fit(ds, epochs=500, steps_per_epoch=dstep,
          validation_data=validation_ds, validation_steps=vstep,
          callbacks=[tensorboard_callback,
                    #  Metrics(valid_data=validation_ds),
                    #  cp_callback,
                     ])
