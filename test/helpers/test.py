from gtts import gTTS
import os
tts = gTTS(text='Guten Morgen', lang='de')
tts.save("good.mp3")

tts = gTTS(text='Die Vierfeldertafel ist damit eine andere Darstellung für ein zweistufiges Baumdiagrammh.', lang='de')
tts.save("artefact_diagramm.mp3")


