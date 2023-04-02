import os.path
from typing import Optional



class Mediafile:

    def __init__(self, file_path: str):
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
        self._get_file_name()
        self._get_file_directory_path()
        self._get_file_extension()
        self._get_number_of_video_streams()
        self._get_number_of_audio_streams()
        self._get_video_streams_info()
        self._get_audio_streams_info()
        self._get_video_scenes()
        self._get_audio_dictation()

    def _get_file_name(self):
        self.file_name = os.path.basename(self.file_path)

    def _get_file_directory_path(self):
        self.file_directory_path = os.path.dirname(self.file_path)

    def _get_file_extension(self):
        return self.file_name.split(".")[-1]

    def _get_number_of_video_streams(self):
        pass

    def _get_number_of_audio_streams(self):
        pass

    def _get_video_streams_info(self):
        pass

    def _get_audio_streams_info(self):
        pass

    def _get_video_scenes(self):
        pass

    def _get_audio_dictation(self):
        pass