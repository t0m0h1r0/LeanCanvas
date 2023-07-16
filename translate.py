import requests
from ruamel.yaml import YAML
import argparse


class Translator:
    def __init__(self, api_key, target_lang='EN', max_chunk_size=5000):
        """
        翻訳APIの抽象クラスです。

        :param api_key: 翻訳APIの認証キー
        :param target_lang: 翻訳対象の言語コード（デフォルトは英語）
        :param max_chunk_size: 翻訳の分割上限文字数（デフォルトは5000）
        """
        self.api_key = api_key
        self.target_lang = target_lang
        self.max_chunk_size = max_chunk_size

    def translate_text(self, text):
        """
        テキストを翻訳します。具象クラスでオーバーライドして実装してください。

        :param text: 翻訳するテキスト
        :return: 翻訳後のテキスト
        """
        raise NotImplementedError()

    def translate_text_list(self, text_list):
        """
        複数のテキストを翻訳します。

        :param text_list: 翻訳するテキストのリスト
        :return: 翻訳後のテキストのリスト
        """
        translated_text_list = []
        chunk, chunk_size = [], 0

        for text in text_list:
            text_len = len(text)

            if chunk_size + text_len <= self.max_chunk_size:
                chunk.append(text)
                chunk_size += text_len
            else:
                translated_chunk = self.translate_text('\n'.join(chunk))
                translated_text_list.extend(translated_chunk.split('\n'))
                chunk = [text]
                chunk_size = text_len

        if chunk:
            translated_chunk = self.translate_text('\n'.join(chunk))
            translated_text_list.extend(translated_chunk.split('\n'))

        return translated_text_list


class DeepLTranslator(Translator):
    def __init__(self, api_key, target_lang='EN', max_chunk_size=5000):
        """
        DeepL APIを使用してテキストを翻訳する具象クラスです。

        :param api_key: DeepL APIの認証キー
        :param target_lang: 翻訳対象の言語コード（デフォルトは英語）
        :param max_chunk_size: 翻訳の分割上限文字数（デフォルトは5000）
        """
        super().__init__(api_key, target_lang, max_chunk_size)
        self.url = "https://api-free.deepl.com/v2/translate"

    def translate_text(self, text):
        """
        テキストをDeepL APIを使用して翻訳します。

        :param text: 翻訳するテキスト
        :return: 翻訳後のテキスト
        """
        response = requests.post(
            self.url,
            data={
                'auth_key': self.api_key,
                'text': text,
                'target_lang': self.target_lang,
            },
        )
        return response.json()["translations"][0]["text"]

class GoogleTranslator(Translator):
    def __init__(self, api_key, target_lang='EN', max_chunk_size=5000):
        """
        Google Translation APIを使用してテキストを翻訳する具象クラスです。

        :param api_key: Google Translation APIの認証キー
        :param target_lang: 翻訳対象の言語コード（デフォルトは英語）
        :param max_chunk_size: 翻訳の分割上限文字数（デフォルトは5000）
        """
        super().__init__(api_key, target_lang, max_chunk_size)
        self.url = "https://translation.googleapis.com/language/translate/v2"

    def translate_text(self, text):
        """
        テキストをGoogle Translation APIを使用して翻訳します。

        :param text: 翻訳するテキスト
        :return: 翻訳後のテキスト
        """
        response = requests.post(
            self.url,
            data={
                'key': self.api_key,
                'q': text,
                'target': self.target_lang,
                'format': 'text'
            },
        )
        return response.json()["data"]["translations"][0]["translatedText"]

class DataTranslator:
    def parse_to_text(self, data):
        """
        データをテキスト形式に変換します。

        :param data: 変換するデータ
        :return: テキスト形式に変換されたデータ（テキストのリスト）
        """
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
        """
        翻訳後のテキストを元のデータ形式に戻します。

        :param data: 元のデータ
        :param translated_lines: 翻訳後のテキストのリスト
        """
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
        """
        YAMLファイルを読み込みます。

        :param filename: 読み込むファイル名
        :return: 読み込まれたデータ
        """
        with open(filename) as file:
            return self.yaml.load(file)

    def dump(self, data, filename):
        """
        データをYAMLファイルに書き込みます。

        :param data: 書き込むデータ
        :param filename: 書き込むファイル名
        """
        with open(filename, 'w') as file:
            self.yaml.dump(data, file)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Translate a YAML file using the DeepL API.")
    parser.add_argument("--input", default="sample.yaml", help="Input YAML file name.")
    parser.add_argument("--output", default="sample_en.yaml", help="Output YAML file name.")
    parser.add_argument("--api_key", required=True, help="DeepL API key.")
    parser.add_argument("--max_chunk_size", default=5000, type=int, help="Maximum chunk size for translation.")
    args = parser.parse_args()
    return args


def translate_file(input_file, output_file, api_key, max_chunk_size):
    """
    入力ファイルを翻訳して出力ファイルに保存します。

    :param input_file: 入力ファイル名
    :param output_file: 出力ファイル名
    :param api_key: DeepL APIの認証キー
    :param max_chunk_size: 翻訳の分割上限文字数
    """
    translator = DeepLTranslator(api_key, max_chunk_size=max_chunk_size)
    data_translator = DataTranslator()
    yaml_handler = YamlHandler()

    data = yaml_handler.load(input_file)
    lines = data_translator.parse_to_text(data)
    translated_lines = translator.translate_text_list(lines)
    data_translator.restore_from_text(data, translated_lines)
    yaml_handler.dump(data, output_file)

if __name__ == "__main__":
    args = parse_arguments()
    translate_file(args.input, args.output, args.api_key, args.max_chunk_size)