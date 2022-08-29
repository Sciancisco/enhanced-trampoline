import os
from string import Formatter

from qira_parser import parse_qira_dat, write_routine_json


class SaveDataError(Exception):
    pass


class SaveData:
    def __init__(self, qira_data_directory, save_data_directory, filename_format, video_container):
        if not os.path.isdir(qira_data_directory):
            raise SaveDataError(f"Given Qira data directory is invalid ('{qira_data_directory}').")

        self._qira_data_directory = qira_data_directory

        if not os.path.isdir(save_data_directory):
            raise SaveDataError(f"Given save data directory is invalid ('{save_data_directory}').")

        self._save_data_directory = save_data_directory

        save_video_directory = save_data_directory + os.sep + "video"
        if os.path.exists(save_video_directory):
            if not os.path.isdir(save_video_directory):
                raise SaveDataError(f"'{save_video_directory}' is not a directory.")
        else:
            os.makedirs(save_video_directory)

        self._save_video_directory = save_video_directory

        save_recovered_directory = save_data_directory + os.sep + "recovered"
        if os.path.exists(save_recovered_directory):
            if not os.path.isdir(save_recovered_directory):
                raise SaveDataError(f"'{save_recovered_directory}' is not a directory.")
        else:
            os.makedirs(save_recovered_directory)

        self._save_recovered_directory = save_recovered_directory

        self._filename_format = filename_format
        self._format_keywords = set(map(lambda t: t[1], Formatter.parse(filename_format)))
        self._video_container = video_container

    def _valid_kwargs(self, kwargs):
        return set(kwargs.keys()) == self._format_keywords

    def _gen_video_filename(self, **kwargs):
        if self._valid_kwargs(kwargs):
            return "".join(
                [
                    self._save_video_directory
                    + os.sep
                    + self._filename_format.format(**kwargs)
                    + "."
                    + self._video_container
                ]
            )

    def gen_video_filename(self, **kwargs):
        return self._gen_video_filename(**kwargs)

    def gen_recovered_filename(self, **kwargs):
        if self._valid_kwargs(kwargs):
            return "".join(
                [
                    self._save_recovered_directory
                    + os.sep
                    + self._filename_format.format(**kwargs)
                    + "_recovered."
                    + self._video_container
                ]
            )

    def dat_to_json(self, **kwargs):
        if not self._valid_kwargs(kwargs):
            raise SaveDataError(f"Expected keywords {self._format_keywords}, got {set(kwargs.key())}.")

        filename_dat = self._qira_data_directory + os.sep + self._filename_format.format(**kwargs) + ".dat"
        data = parse_qira_dat(filename_dat)

        if os.path.isfile(self._gen_video_filename(**kwargs)):  # link video, if video there is
            data["meta"]["video"] = self._filename_format.format(**kwargs) + "." + self._video_container

        filename_json = self._save_data_directory + os.sep + self._filename_format.format(**kwargs) + ".json"
        write_routine_json(filename_json, data)
