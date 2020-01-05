from gtts import gTTS
import moviepy.audio.io.AudioFileClip
import moviepy.audio.fx.volumex

tts = gTTS(text="blahh blaahh bla and blablabla and blablablablablabla", lang="en")
tts.save("audio_async.mp3")

audio_clip = moviepy.audio.io.AudioFileClip.AudioFileClip("audio_async.mp3")
audio_clip = audio_clip.fx(moviepy.audio.fx.volumex.volumex, 0.1)
audio_clip.write_audiofile("audio_async.mp3")
#test = audio_clip.fx(moviepy.audio.fx.volumex.volumex, 0.5)

tts = gTTS(text="Audio-Test", lang="en")
tts.save("audio.mp3")
