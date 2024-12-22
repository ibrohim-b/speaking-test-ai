from typing import Any
from dataclasses import dataclass


@dataclass
class FirstIelts:
    id: int = 0
    duration: int = 0
    content: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'FirstIelts':
        _id = int(obj.get("id"))
        _duration = int(obj.get("duration"))
        _content = str(obj.get("content"))
        return FirstIelts(_id, _duration, _content)


@dataclass
class SecondIelts:
    id: int = 0
    duration: int = 0
    content: str = ""
    followup: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'SecondIelts':
        _id = int(obj.get("id"))
        _duration = int(obj.get("duration"))
        _content = str(obj.get("content"))
        _followup = str(obj.get("followup"))
        return SecondIelts(_id, _duration, _content, _followup)


@dataclass
class ThirdIelts:
    id: int = 0
    duration: int = 0
    content: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'ThirdIelts':
        _id = int(obj.get("id"))
        _duration = int(obj.get("duration"))
        _content = str(obj.get("content"))
        return ThirdIelts(_id, _duration, _content)


@dataclass
class IeltsSample:
    id: int
    first: FirstIelts
    second: SecondIelts
    third: ThirdIelts

    @staticmethod
    def from_dict(obj: Any) -> 'IeltsSample':
        _id = int(obj.get("id"))
        _first = FirstIelts.from_dict(obj.get("first"))
        _second = SecondIelts.from_dict(obj.get("second"))
        _third = ThirdIelts.from_dict(obj.get("third"))
        return IeltsSample(_id, _first, _second, _third)


@dataclass
class FirstToefl:
    id: int = 0
    preparation: int = 15
    speach: int = 45
    content: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'FirstToefl':
        _id = int(obj.get("id"))
        _preparation = int(obj.get("preparation"))
        _speach = int(obj.get("speach"))
        _content = str(obj.get("content"))
        return FirstToefl(_id, _preparation, _speach, _content)


@dataclass
class FourthToefl:
    id: int = 0
    preparation: int = 0
    speach: int = 0
    content: str = ""
    audio: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'FourthToefl':
        _id = int(obj.get("id"))
        _preparation = int(obj.get("preparation"))
        _speach = int(obj.get("speach"))
        _content = str(obj.get("content"))
        _audio = str(obj.get("audio"))
        return FourthToefl(_id, _preparation, _speach, _content, _audio)


@dataclass
class SecondToefl:
    id: int = 0
    preparation: int = 0
    reading: int = 0
    speach: int = 0
    content: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'SecondToefl':
        _id = int(obj.get("id"))
        _preparation = int(obj.get("preparation"))
        _reading = int(obj.get("reading"))
        _speach = int(obj.get("speach"))
        _content = str(obj.get("content"))
        return SecondToefl(_id, _preparation, _reading, _speach, _content)


@dataclass
class ThirdToefl:
    id: int = 0
    preparation: int = 0
    reading: int = 0
    speach: int = 0
    content: str = ""

    @staticmethod
    def from_dict(obj: Any) -> 'ThirdToefl':
        _id = int(obj.get("id"))
        _preparation = int(obj.get("preparation"))
        _reading = int(obj.get("reading"))
        _speach = int(obj.get("speach"))
        _content = str(obj.get("content"))
        return ThirdToefl(_id, _preparation, _reading, _speach, _content)


@dataclass
class ToeflSample:
    id: int
    first: FirstToefl
    second: SecondToefl
    third: ThirdToefl
    fourth: FourthToefl

    @staticmethod
    def from_dict(obj: Any) -> 'ToeflSample':
        _id = int(obj.get("id"))
        _first = FirstToefl.from_dict(obj.get("first"))
        _second = SecondToefl.from_dict(obj.get("second"))
        _third = ThirdToefl.from_dict(obj.get("third"))
        _fourth = FourthToefl.from_dict(obj.get("fourth"))
        return ToeflSample(_id, _first, _second, _third, _fourth)


@dataclass
class IeltsAnswer:
    message: str
    content: str
    sample_id: int

    @staticmethod
    def from_dict(obj: Any) -> 'IeltsAnswer':
        _message = str(obj.get("message"))
        _content = str(obj.get("content"))
        _sample_id = int(obj.get("sample_id"))
        return IeltsAnswer(_message, _content, _sample_id)

@dataclass
class ToeflAnswer:
    message: str
    content: str
    sample_id: int

    @staticmethod
    def from_dict(obj: Any) -> 'ToeflAnswer':
        _message = str(obj.get("message"))
        _content = str(obj.get("content"))
        _sample_id = int(obj.get("sample_id"))
        return ToeflAnswer(_message, _content, _sample_id)

@dataclass
class IeltsAskAI:
    message: str
    content: str
    audio: str
    context: str

    @staticmethod
    def from_dict(obj: Any) -> 'IeltsAskAI':
        _message = str(obj.get("message"))
        _content = str(obj.get("content"))
        _audio = str(obj.get("audio"))
        _context = str(obj.get("context"))
        return IeltsAskAI(_message, _content, _audio, _context)
