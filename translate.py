import requests
from ruamel.yaml import YAML
import argparse

class DeepLTranslator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api-free.deepl.com/v2/translate"

    def translate(self, text):
        response = requests.post(
            self.url,
            data={
                'auth_key': self.api_key,
                'text': text,
                'target_lang': 'EN',
            },
        )
        return response.json()["translations"][0]["text"]

    def translate_text_list(self, text_list):
        chunk, chunk_size = [], 0
        translated_text_list = []

        for text in text_list:
            text_len = len(text)
            if chunk_size + text_len <= 5000:
                chunk.append(text)
                chunk_size += text_len
            else:
                translated_chunk = self.translate('\n'.join(chunk))
                translated_text_list.extend(translated_chunk.split('\n'))
                chunk = [text]
                chunk_size = text_len

        if chunk:
            translated_chunk = self.translate('\n'.join(chunk))
            translated_text_list.extend(translated_chunk.split('\n'))

        return translated_text_list

class DataTranslator:
    def parse_to_text(self, data):
        lines = []
        self._parse_to_text_recursive(data, lines)
        return lines

    def _parse_to_text_recursive(self, data, lines):
        if isinstance(data, dict):
            for v in data.values():
                self._parse_to_text_recursive(v, lines)
        elif isinstance(data, list):
            for v in data:
                self._parse_to_text_recursive(v, lines)
        elif isinstance(data, str):
            lines.append(data)

    def restore_from_text(self, data, translated_lines):
        self._restore_from_text_recursive(data, iter(translated_lines))

    def _restore_from_text_recursive(self, data, translated_lines):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = next(translated_lines)
                else:
                    self._restore_from_text_recursive(v, translated_lines)
        elif isinstance(data, list):
            for i in range(len(data)):
                if isinstance(data[i], str):
                    data[i] = next(translated_lines)
                else:
                    self._restore_from_text_recursive(data[i], translated_lines)

class YamlHandler:
    def __init__(self):
        self.yaml = YAML()

    def load(self, filename):
        with open(filename) as file:
            return self.yaml.load(file)

    def dump(self, data, filename):
        with open(filename, 'w') as file:
            self.yaml.dump(data, file)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Translate a YAML file using the DeepL API.")
    parser.add_argument("--input", default="sample.yaml", help="Input YAML file name.")
    parser.add_argument("--output", default="sample_en.yaml", help="Output YAML file name.")
    parser.add_argument("--api_key", required=True, help="DeepL API key.")
    args = parser.parse_args()
    return args

def translate_file(input_file, output_file, api_key):
    translator = DeepLTranslator(api_key)
    data_translator = DataTranslator()
    yaml_handler = YamlHandler()

    data = yaml_handler.load(input_file)
    lines = data_translator.parse_to_text(data)
    translated_lines = translator.translate_text_list(lines)
    data_translator.restore_from_text(data, translated_lines)
    yaml_handler.dump(data, output_file)

if __name__ == "__main__":
    args = parse_arguments()
    translate_file(args.input, args.output, args.api_key)
