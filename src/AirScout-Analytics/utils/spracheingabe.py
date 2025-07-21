#spracheingabe tool




import speech_recognition as sr

def filter_woerter(audioquelle, suchwoerter):
    erkenner = sr.Recognizer()
    with sr.Microphone() as quelle:
        print("Sprich jetzt...")
        audio = erkenner.listen(quelle)
    try:
        text = erkenner.recognize_google(audio, language="de-DE")
        print("Erkannt:", text)
        gefundene = [wort for wort in suchwoerter if wort in text]
        print("Gefundene Wörter:", gefundene)
        return gefundene
    except Exception as e:
        print("Fehler:", e)
        return []

if __name__ == "__main__":
    # Code hier drunter wird nur ausgeführt wenn das Skript direkt aufgerufen wird
    # Beispielaufruf:
    filter_woerter(sr.Microphone(), ["Python", "Test", "Hallo"])
    pass