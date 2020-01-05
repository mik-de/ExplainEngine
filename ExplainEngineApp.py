from gtts import gTTS
import os
import os.path
import argparse
from PIL import Image
import moviepy.video.VideoClip
import moviepy.audio.AudioClip
import moviepy.audio.io.AudioFileClip
import moviepy.editor
import numpy
import tempfile

def AppendClip(clip, clip_appended):
	if clip is not None:
		clip = moviepy.editor.concatenate_videoclips([clip, clip_appended])
	else:
		clip = clip_appended
	return clip

def AsyncAudio(offset, filename):
	return 	{"offset" : offset, "filename" : filename}

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--language", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()


input_filename = args.input
language = args.language
output_filename = os.path.abspath(args.output)
workspace = os.path.abspath( os.path.dirname(input_filename))
current_work_directory = os.getcwd()
os.chdir(workspace)
input_filename=os.path.basename(input_filename)
with open(input_filename) as f:
    content = f.readlines()
# Remove whitespace characters at the end and the beginning of each line
content = [x.strip() for x in content] 
# Remove empty lines
# content = list(filter(None, content))

counter = 0
async_audios = list()

wallpaper = Image.new("RGBA", [1920, 1080])
clip = None

for line in content:
	counter += 1
	print("> Line " + str(counter) + ": " + line)
	if not line:
		pause=0.33
		print("Auto pausing for (sec): " + str(pause))
		segment_clip = moviepy.video.VideoClip.ImageClip(numpy.array(wallpaper),
				duration=pause)
		clip = AppendClip(clip, segment_clip)
		continue # empty lines are short pauses
	if line[:2] == '//':
		print("Skipping comment: " + line[2:].strip())
		continue
	if line[:1] == '[':
		[element, parameter] = line[1:].split(']')
		parameter = parameter[1:-1].strip()
		tag = element.split('|')[0].strip()
		attributes = element.split('|')[1:]
		# print("Parsing element: " + element)
		print("Parsing tag: " + tag)
		print("Parsing parameter: " + parameter)
		if tag == "img":
			# update only the wallpaper and no clip
			new_layer = Image.open(parameter)
			wallpaper.paste(new_layer, (0, 0), new_layer)			
		elif tag == "audio" and not "async" in attributes:
			print("Inserting an audio clip")
			audio_clip = moviepy.audio.io.AudioFileClip.AudioFileClip(parameter)
			segment_clip = moviepy.video.VideoClip.ImageClip(numpy.array(wallpaper),
					duration=audio_clip.duration)
			segment_clip.audio = audio_clip
			clip = AppendClip(clip, segment_clip)
			audio_clip = None
			segment_clip = None
		elif tag == "audio":
			print("Adding an async audio clip")
			offset = 0
			if clip is not None:
				offset = clip.duration
			async_audios.append(AsyncAudio(offset, parameter))
		elif tag == "pause":
			pause = float(attributes[0])
			print("Pausing for (sec): " + str(pause))
			segment_clip = moviepy.video.VideoClip.ImageClip(numpy.array(wallpaper),
					duration=pause)
			clip = AppendClip(clip, segment_clip)
			segment_clip = None
		else:
			raise Exception("Invalid tag: " + tag)	
		continue
	
	tts = gTTS(text=line, lang=language)
	temp_fp = tempfile.NamedTemporaryFile(suffix='.mp3') # FFmpeg needs files in filesystem
	tts.write_to_fp(temp_fp)
	temp_fp.flush()
	print(temp_fp.name)
	tts_clip = moviepy.audio.io.AudioFileClip.AudioFileClip(temp_fp.name)
	segment_clip = moviepy.video.VideoClip.ImageClip(numpy.array(wallpaper), duration=tts_clip.duration)
	segment_clip.audio = tts_clip
	clip = AppendClip(clip, segment_clip)
	segment_clip = None
	tts = None
	temp_fp = None

if async_audios:
	print("Mixing async audio")
for async_audio in async_audios:
	print("Async Audio: " + str(async_audio))
	duration = clip.duration
	audio_clip = moviepy.audio.io.AudioFileClip.AudioFileClip(async_audio["filename"])
	clip.audio = moviepy.audio.AudioClip.CompositeAudioClip(
			[clip.audio, audio_clip.set_start(async_audio["offset"])] )
	clip.duration = duration # preserve duration and cut async audio
	audio_clip = None


print("Rendering video")
os.chdir(current_work_directory)
clip.write_videofile(output_filename, fps=30)


# Basic Syntax:
# // comment
# [img]() // png only
# [audio|async]()
# [pause|10] 
# Default screen size 1920x1080

# Planned: video # // + fade_in?

# Syntax:
# [img|id:xxx|fade_in|stack:name|top:#|background:#|position](filename)
# [stack|new:name|stack_prev] // default last stack
# [show_stack|on/off:name,name or all]
# [goto_stack|name]
# [audio|async:offset](filename)
# [pause](10s)
# [clear|id:xxx]
# [lang|de|pop|default]
# [video|mix|cut:xx,xx]
# [waitfor|timeout:time]
# [dict|word:ssml|word:ssml]
# pronuounciation dictionary
# speed
# [meta|...]
# // comment
# screen size?
# ssml?
# functions/macros/external?
