Vosk-Zundamon
====

Connect Vosk (Speech Recognition) and Zundamon (Text-to-speech application, VOICEVOX).

# Installation

1. Download & extract `vosk-model-small-ja-0.22` from https://alphacephei.com/vosk/models and save it to `resource/`
2. Download & extract `open_jtalk_dic_utf_8-1.11` from http://open-jtalk.sourceforge.net/ and save it to `resource/`
3. `pip install -r requirements.txt`
4. Follow the instruction of voicevox_core and install 0.12.0-preview.3 or later.

# Usage

`python mic.py`

# Note
GPU may accelerate the speed of translation. See README in voicevox_core and change the arguments of the initialize function.

# License
See [LICENSE](./LICENSE)