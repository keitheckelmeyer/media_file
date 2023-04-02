import os.path, logging
import traceback
from typing import Optional
import skvideo, skvideo.io
# Standard PySceneDetect imports:
from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

from vosk import Model, KaldiRecognizer, SetLogLevel
import os, json
import subprocess


class Mediafile:

    def __init__(self, file_path: str, vosk_model: str = "model_128M"):
        self.file_path = file_path
        self.file_name = Optional[str]
        self.file_directory_path = Optional[str]
        self.file_extension = Optional[str]
        self.number_of_video_streams = Optional[int]
        self.number_of_audio_streams = Optional[int]
        self.video_streams_info = Optional[dict]
        self.audio_streams_info = Optional[dict]
        self.video_scenes = Optional[dict]
        self.audio_dictation = Optional[dict]
        self.vosk_model = vosk_model

    def initialize(self):
        self._get_file_name()
        self._get_file_directory_path()
        self._get_file_extension()
        self._process_audio_streams()
        self._process_video_streams()
        self._get_audio_dictation()
        self._get_video_scenes()
        
    def to_dict(self):
        d = {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_directory_path": self.file_directory_path,
            "file_extension": self.file_extension,
            "number_of_video_streams": self.number_of_video_streams,
            "number_of_audio_streams": self.number_of_audio_streams,
            "video_streams_info": self.video_streams_info,
            "audio_dictation": self.audio_dictation,
            }
        return d

    def _get_file_name(self):
        self.file_name = os.path.basename(self.file_path)

    def _get_file_directory_path(self):
        self.file_directory_path = os.path.dirname(self.file_path)

    def _get_file_extension(self):
        self.file_extension = self.file_name.split(".")[-1].lower()

    def _process_streams(self, stream_type: str):
        meta_data = skvideo.io.ffprobe(self.file_path)
        i = 0
        data = {}
        for key in meta_data.keys():
            if str(key).lower().find(stream_type) >= 0:
                i += 1
                this_dict = {}
                for k, v in meta_data[key].items():
                    this_dict[k] = v
                data[i] = this_dict
        return data, i

    def _process_video_streams(self):
        data, streams = self._process_streams("video")
        self.video_streams_info = data
        self.number_of_video_streams = streams

    def _process_audio_streams(self):
        data, streams = self._process_streams("audio")
        self.audio_streams_info = data
        self.number_of_audio_streams = streams

    def _get_video_scenes(self):
        logging.info(f"Starting Scene Detection for: {self.file_name}")
        video_manager = VideoManager([self.file_path])

        t_list = [30, 50, 70, 90]
        # Improve processing speed by downscaling before processing.
        video_manager.set_downscale_factor()
        data = {}
        for t in t_list:
            logging.info(f"Starting Scene Detection at level: {str(t)}")
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=t))
            # Start the video manager and
            # perform the scene detection.
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            # Each returned scene is a tuple of the (start, end) timecode.
            scene_list = scene_manager.get_scene_list()
            scene_data = {}
            for n, scene in enumerate(scene_list):
                scene_data[n+1] = scene
            data[t] = scene_data
        self.video_scenes = data
        logging.info(f"Completed Scene Detection for: {self.file_name}")
        
    def _get_audio_dictation(self):
        logging.info(f"Starting audio transcription for: {self.file_name}")
        try:
            SetLogLevel(0)

            if not os.path.exists("model"):
                print(
                    "Please download the model from https://alphacephei.com/vosk/models and "
                    "unpack as 'model' in the current folder.")

            sample_rate = 16000
            model = Model(self.vosk_model)
            rec = KaldiRecognizer(model, sample_rate)
            audio_data = {}
            for i in range(self.number_of_audio_streams):
                logging.info(f"Starting audio stream {i+1} of {self.number_of_audio_streams}.")
                audio_channel = i + 1

                process = subprocess.Popen(['ffmpeg',
                                            '-loglevel', 'quiet',
                                            '-i', self.file_path,
                                            '-ar', str(sample_rate),
                                            '-ac', str(audio_channel),
                                            '-f', 's16le', '-'],
                                           stdout=subprocess.PIPE)

                """
                x = r'{"text": ""}'
                print("test")
                print(x)
                print("end test")
                """
                r_list = []
                while True:
                    data = process.stdout.read(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        # print(f"result***\n {rec.Result()}")
                        try:
                            r = json.loads(rec.Result())
                            # print(r['result'])
                            if 'result' in r:
                                d = {'result': r['result'],
                                     'text': r['text']}
                                r_list.append(d)
                                # r_list.append(r)
                                # print(r['result'])
                                # print(r['text'])
                            # print(rec.Result())
                            # print(rec.Result())
                        except:
                            pass
                audio_data[audio_channel] = r_list
                logging.info(f"Completed audio stream {i + 1} of {self.number_of_audio_streams}.")
            self.audio_dictation = audio_data
            logging.info(f"Completed audio transcription for: {self.file_name}")

        except:
            print(traceback.format_exc())
            print()
