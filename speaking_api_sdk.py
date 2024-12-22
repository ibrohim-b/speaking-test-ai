import requests
import json

from models import IeltsSample, ToeflSample, IeltsAnswer, ToeflAnswer, IeltsAskAI


class SpeakingApiSdk:
    def __init__(self):
        self.base_url = 'http://steblan.online:5252'

    def get_ielts_sample(self, sample_id):
        json_data = {}
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.get(
            f'{self.base_url}/ielts/sample/{sample_id}',
            headers=headers,
            json=json_data,
        )

        match response.status_code:
            case 200:
                json_dict = json.loads(response.text)
                sample = IeltsSample.from_dict(json_dict)
                return sample

    def get_toefl_sample(self, sample_id):
        json_data = {}
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.get(
            f'{self.base_url}/toefl/sample/{sample_id}',
            headers=headers,
            json=json_data,
        )

        match response.status_code:
            case 200:
                json_dict = json.loads(response.text)
                sample = ToeflSample.from_dict(json_dict)
                return sample

    def answer_ielts(self, file_path, file_name, sample_id):

        payload = {"sample": sample_id}
        files = [
            ('audio',
             (file_name, open(file_path, 'rb'), 'audio/mpeg'))
        ]
        headers = {}

        response = requests.post(f"{self.base_url}/ielts/answer/", files=files, data=payload)

        match response.status_code:
            case 200:
                json_dict = json.loads(response.text)
                sample = IeltsAnswer.from_dict(json_dict)
                return sample

    def answer_toefl(self, file_path, file_name, sample_id):

        payload = {"sample": f"{sample_id}"}
        files = [
            ('audio',
             (file_name, open(file_path, 'rb'), 'audio/mpeg'))
        ]
        headers = {}

        response = requests.post(f"{self.base_url}/toefl/answer/", files=files, data=payload)

        match response.status_code:
            case 200:
                json_dict = json.loads(response.text)
                sample = ToeflAnswer.from_dict(json_dict)
                return sample

    def ask_ai_ielts(self, context, audio) -> IeltsAskAI:
        payload = {"context": context}
        files = [
            ('audio',
             (audio, open(audio, 'rb'), 'audio/mpeg'))
        ]
        headers = {}

        response = requests.post(f"{self.base_url}/ielts/question/", files=files, data=payload)
        print(response.text)
        match response.status_code:
            case 200:
                json_dict = json.loads(response.text)
                ieltsAskAi = IeltsAskAI.from_dict(json_dict)
                return ieltsAskAi
