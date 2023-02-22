import re
import tensorflow as tf
from tensorflow import keras

# Załadowanie zbioru danych zawierającego przykłady ataków SQL Injection oraz zapytań niewrażliwych na atak
data = open('sql_injection_dataset.txt', 'r').readlines()
X, y = [], []
for i in range(len(data)):
    if i % 2 == 0:
        X.append(data[i].strip())
    else:
        y.append(int(data[i].strip()))

# Przygotowanie danych treningowych i testowych
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Przygotowanie sekwencera tekstu dla danych wejściowych
tokenizer = keras.preprocessing.text.Tokenizer(char_level=True)
tokenizer.fit_on_texts(X_train)

# Zamiana zdań na ciągi liczb reprezentujących pojedyncze znaki
X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

# Dopasowanie sekwencera tekstu do maksymalnej długości zapytania
max_length = 500
X_train = keras.preprocessing.sequence.pad_sequences(X_train, maxlen=max_length, padding='post')
X_test = keras.preprocessing.sequence.pad_sequences(X_test, maxlen=max_length, padding='post')

# Budowa i trenowanie modelu
model = keras.Sequential([
    keras.layers.Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=32, input_length=max_length),
    keras.layers.Bidirectional(keras.layers.LSTM(32)),
    keras.layers.Dense(1, activation='sigmoid')
])
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=64)

# Ocena modelu na danych testowych
loss, accuracy = model.evaluate(X_test, y_test)
print('Test accuracy:', accuracy)

# Przygotowanie zapytania do klasyfikacji
query = "SELECT * FROM users WHERE username='admin' AND password='123456'"

# Przekonwertowanie zapytania na sekwencję liczbową i dopasowanie do maksymalnej długości
query_seq = tokenizer.texts_to_sequences([query])
query_padded = keras.preprocessing.sequence.pad_sequences(query_seq, maxlen=max_length, padding='post')

# Klasyfikacja zapytania przy użyciu wytrenowanego modelu
prediction = model.predict(query_padded)[0][0]

# Wyświetlenie wyniku klasyfikacji
if prediction < 0.5:
    print('Zapytanie jest bezpieczne.')
else:
    print('Zapytanie jest atakiem SQL Injection!')
