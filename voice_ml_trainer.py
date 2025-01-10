import os
import numpy as np
import librosa
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB


def extract_features(audio_path):
    """Ses dosyasından özellik çıkarma"""
    # Ses dosyasını yükle
    audio, sr = librosa.load(audio_path, duration=1.5)
    
    # Çeşitli özellikler çıkar
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    mel = librosa.feature.melspectrogram(y=audio, sr=sr)
    
    # Özelliklerin ortalamasını ve standart sapmasını al
    mfccs_mean = np.mean(mfccs.T, axis=0)
    mfccs_std = np.std(mfccs.T, axis=0)
    chroma_mean = np.mean(chroma.T, axis=0)
    mel_mean = np.mean(mel.T, axis=0)
    
    # Tüm özellikleri birleştir
    features = np.concatenate([mfccs_mean, mfccs_std, chroma_mean, mel_mean])
    return features

def load_dataset(data_path):
    """Veri setini yükle ve özellikleri çıkar"""
    features = []
    labels = []
    # Klasör isimleri ve çıktı etiketleri arasındaki eşleştirme
    command_mapping = {
        "parlaklik_ac": "parlaklik_ac",
        "parlaklik_kapat": "parlaklik_kapat",
        "ses_ac": "ses_ac",
        "ses_kapat": "ses_kapat",
        "ekran_goruntusu": "ekran_goruntusu"
    }
    
    # Her komut klasörü için
    for command in os.listdir(data_path):
        command_path = os.path.join(data_path, command)
        if os.path.isdir(command_path):
            # Her ses dosyası için
            for audio_file in os.listdir(command_path):
                if audio_file.endswith('.wav'):
                    file_path = os.path.join(command_path, audio_file)
                    
                    # Özellikleri çıkar
                    feature_vector = extract_features(file_path)
                    features.append(feature_vector)
                    labels.append(command_mapping[command])
    
    return np.array(features), np.array(labels)

def train_models(features, labels):
    """Random Forest ve SVM modellerini eğit"""
    # Veriyi eğitim ve test setlerine ayır
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.33, random_state=42, stratify=labels
    )
    
    # Özellikleri ölçeklendir
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Random Forest modeli
    rf_model = RandomForestClassifier(
        n_estimators=5,
        max_depth=2,
        random_state=42
    )
    rf_model.fit(X_train_scaled, y_train)
    rf_pred = rf_model.predict(X_test_scaled)
    
    # SVM modeli
    svm_model = SVC(kernel='rbf', probability=True)
    svm_model.fit(X_train_scaled, y_train)
    svm_pred = svm_model.predict(X_test_scaled)
    
    knn_model = KNeighborsClassifier(n_neighbors=5)
    knn_model.fit(X_train_scaled, y_train)
    knn_pred = knn_model.predict(X_test_scaled)
    
    # Gradient Boosting modeli
    gbc_model = GradientBoostingClassifier(random_state=42)
    gbc_model.fit(X_train_scaled, y_train)
    gbc_pred = gbc_model.predict(X_test_scaled)
    
    # Logistic Regression modeli
    lr_model = LogisticRegression(random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    lr_pred = lr_model.predict(X_test_scaled)
    
    # Naive Bayes modeli
    nb_model = GaussianNB()
    nb_model.fit(X_train_scaled, y_train)
    nb_pred = nb_model.predict(X_test_scaled)
        
    # Sonuçları değerlendir
    print("Random Forest Sonuçları:")
    print(classification_report(y_test, rf_pred))
    print("\nSVM Sonuçları:")
    print(classification_report(y_test, svm_pred))
    print("\nKNN Sonuçları:")
    print(classification_report(y_test, knn_pred))
    print("\nGBC Sonuçları:")
    print(classification_report(y_test, gbc_pred))
    print("\nLR Sonuçları:")
    print(classification_report(y_test, lr_pred))
    print("\nNB Sonuçları:")
    print(classification_report(y_test, nb_pred))
    
    return rf_model, svm_model, knn_model, gbc_model, lr_model, nb_model, scaler

def predict_command(audio_path, model, scaler):
    """Yeni ses kaydı için tahmin yap"""
    # Özellikleri çıkar ve ölçeklendir
    features = extract_features(audio_path)
    features_scaled = scaler.transform(features.reshape(1, -1))
    
    # Tahmin yap
    prediction = model.predict(features_scaled)[0]
    
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(features_scaled)[0]
        confidence = max(probabilities)
        print(f"Tahmin güven oranı: {confidence:.2f}")
    
    return prediction

if __name__ == "__main__":
    # Veri klasörü
    data_path = "data"
    
    # Veriyi yükle ve özellikleri çıkar
    print("Veri yükleniyor ve özellikler çıkarılıyor...")
    features, labels = load_dataset(data_path)
    
    # Modelleri eğit
    print("Modeller eğitiliyor...")
    rf_model, svm_model, knn_model, gbc_model, lr_model, nb_model, scaler = train_models(features, labels)
    
    # Modelleri kaydet
    joblib.dump(rf_model, 'rf_model.joblib')
    joblib.dump(svm_model, 'svm_model.joblib')
    joblib.dump(lr_model, 'lr_model.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    
    # Test klasöründeki dosyaları tahmin et
    test_path = "test"
    print("\nTest klasöründeki dosyalar tahmin ediliyor...")
    
    for test_file in os.listdir(test_path):
        if test_file.endswith('.wav'):
            test_audio_path = os.path.join(test_path, test_file)
            
            print(f"\nSes dosyası: {test_file}")
            
            # Random Forest ile tahmin
            rf_result = predict_command(test_audio_path, rf_model, scaler)
            print(f"Random Forest tahmini: {rf_result}")
            
            # SVM ile tahmin
            svm_result = predict_command(test_audio_path, svm_model, scaler)
            print(f"SVM tahmini: {svm_result}")
            
            knn_result = predict_command(test_audio_path, knn_model, scaler)
            print(f"KNN tahmini: {knn_result}")
            
            gbc_result = predict_command(test_audio_path, gbc_model, scaler)
            print(f"GBC tahmini: {gbc_result}")
            
            lr_result = predict_command(test_audio_path, lr_model, scaler)
            print(f"LR tahmini: {lr_result}")
            
            nb_result = predict_command(test_audio_path, nb_model, scaler)
            print(f"NB tahmini: {nb_result}")
            
