"""
   Copyright 2022 Yosshi999

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys
import json
import queue
from collections import deque
import wave
from io import BytesIO

import sounddevice
import vosk
import numpy as np
import resampy

import core as vvcore

MODEL_PATH = "./resource/vosk-model-small-ja-0.22"
DICT_PATH = "./resource/open_jtalk_dic_utf_8-1.11"
model = vosk.Model(MODEL_PATH)
vvcore.initialize(False, 0)
vvcore.voicevox_load_openjtalk_dict(DICT_PATH)

device_info = sounddevice.query_devices(None, "input")
sample_rate = int(device_info["default_samplerate"])
print("sample_rate", sample_rate)

q = queue.Queue()
outq = deque()

def process(indata, outdata, frames, time, status):
    """This is called from a separate thread for each audio block."""
    if status:
        print("[+]", status, file=sys.stderr)
    q.put(bytes(indata))

    outdata[:] = bytes(len(outdata))
    iteration = 0
    while len(outq) > 0 and iteration < len(outdata):
        data = outq.popleft()
        data_send = data[:len(outdata) - iteration]
        outdata[iteration : iteration + len(data_send)] = data_send
        iteration += len(data_send)
        if len(data) > len(data_send):
            outq.appendleft(data[len(data_send):])

try:
    with sounddevice.RawStream(samplerate=sample_rate,
                               blocksize=8000,
                               device=None,
                               dtype='int16',
                               channels=1,
                               callback=process):
        rec = vosk.KaldiRecognizer(model, sample_rate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result["text"]
                print()
                print("[###]", text)
                text = text.replace(" ", "")
                wavbin = vvcore.voicevox_tts(text, 1)
                wavf = wave.open(BytesIO(wavbin))
                sr = wavf.getframerate()
                data = np.frombuffer(wavf.readframes(wavf.getnframes()), 'int16')
                data = resampy.resample(data, sr, sample_rate)
                outq.append(data.tobytes())
                print("[vvv]", text)
            else:
                result = json.loads(rec.PartialResult())
                sys.stdout.write("\r [...] " + result["partial"])
except KeyboardInterrupt:
    print("\nInterrupted by user")

vvcore.finalize()