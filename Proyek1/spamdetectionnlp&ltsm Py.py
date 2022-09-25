# -*- coding: utf-8 -*-
"""SpamDetectionNLP&LTSM

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kHKXkNZ32vn5eBIfsaSWNwtzw1JbOpwR
"""

!pip install -q kaggle

from google.colab import files
#Upload Kaggle API Key
files.upload()

!mkdir ~/.kaggle #make new directory in root folder
!cp kaggle.json ~/.kaggle/ #copy and paste kaggle API key to new directory
!chmod 600 ~/.kaggle/kaggle.json #permission
!kaggle datasets list

!kaggle datasets download -d venky73/spam-mails-dataset

import os
import zipfile
import pandas as pd
import numpy as np
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, Dense, Dropout, BatchNormalization, Flatten, LSTM
from tensorflow.keras.callbacks import Callback, ReduceLROnPlateau, EarlyStopping
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, classification_report

zipPath = '../content/spam-mails-dataset.zip' #zip path in local 
zipFile = zipfile.ZipFile(zipPath, 'r')
zipFile.extractall('../content/spamMailDataset') #extract to new directory
zipFile.close() #close connection to object

filePath = '../content/spamMailDataset/spam_ham_dataset.csv'
df = pd.read_csv(filePath)
df.head()

df = df.drop(columns = 'Unnamed: 0', axis = 1)

df.info()

# No NaN in the data
df.isna().sum()

#No NULL in the data
df.isnull().sum()

df['label'].value_counts()

stop_words = set(stopwords.words('english')) 

df['text'] = df['text'].apply(lambda x: ' '.join([w for w in x if not w.lower() in stop_words]))

length = df['text'].str.len().max()
X = df['text'].values
y = df['label_num'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

tokenizer = Tokenizer(num_words=length, oov_token='<x>')
tokenizer.fit_on_texts(X_train) 
tokenizer.fit_on_texts(X_test)
 
seq_train = tokenizer.texts_to_sequences(X_train)
seq_test = tokenizer.texts_to_sequences(X_test)
 
padded_train = pad_sequences(seq_train, maxlen=20) 
padded_test = pad_sequences(seq_test, maxlen=20)

#Architecture
model = Sequential([
    Embedding(250, 16, input_length=20),
    LSTM(64),
    Dropout(0.2),
    BatchNormalization(),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Flatten(),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='Adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

#Callback Function
class accCallback(Callback):
   def on_epoch_end(self, epoch, logs={}):
        if(logs.get('accuracy') >= 0.90 and logs.get('val_accuracy') >= 0.90):
            print("\nAccuracy and Val_Accuracy has reached 90%!", "\nEpoch: ", epoch)
            self.model.stop_training = True

callbacks = accCallback()

auto_reduction_LR = ReduceLROnPlateau(
    monitor = 'val_accuracy',
    patience = 2, #if after 2 epoch not improve reduce LR by factor
    verbose = 1,
    factor = 0.2,
    min_lr = 0.000003
)

auto_stop_learn = EarlyStopping(
    monitor = 'val_accuracy',
    min_delta = 0,
    patience = 4,
    verbose = 1,
    mode = 'auto' 
)

History = model.fit(
    padded_train, y_train, 
    epochs = 100, 
    callbacks=[callbacks, auto_reduction_LR, auto_stop_learn], 
    validation_data = (padded_test, y_test),
    verbose = 2
)

plt.plot(History.history['loss'])
plt.plot(History.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'], loc = 'upper right')
plt.show()

plt.plot(History.history['accuracy'])
plt.plot(History.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='lower right')
plt.show()