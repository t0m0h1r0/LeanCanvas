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

    def _translate_text(self, text):
        """
        テキストを翻訳します。具象クラスでオーバーライドして実装してください。

        :param text: 翻訳するテキスト
        :return: 翻訳後のテキスト
        """
        raise NotImplementedError()

    def _split_into_chunks(self, text_list):
        """
        Split the input text list into chunks based on `self.max_chunk_size`.

        :param text_list: List of texts to be translated
        :return: List of text chunks
        """
        if self.max_chunk_size <= 0:
            return [text_list]  # Return the entire text_list as a single chunk

        chunks = []
        chunk, chunk_size = [], 0

        for text in text_list:
            text_len = len(text)

            if chunk_size + text_len <= self.max_chunk_size:
                chunk.append(text)
                chunk_size += text_len
            else:
                chunks.append(chunk)
                chunk = [text]
                chunk_size = text_len

        if chunk:
            chunks.append(chunk)

        return chunks

    def _translate_chunks(self, chunks):
        """
        Translate each chunk in the list of chunks.

        :param chunks: List of text chunks
        :return: List of translated text chunks
        """
        translated_chunks = []
        for chunk in chunks:
            chunk_text = '\n'.join(chunk)
            translated_chunk = self._translate_text(chunk_text)
            translated_chunks.append(translated_chunk.split('\n'))
        return translated_chunks

    def _reassemble_chunks(self, translated_chunks):
        """
        Reassemble the translated text chunks into a list format.

        :param translated_chunks: List of translated text chunks
        :return: List of translated texts
        """
        translated_text_list = [line for chunk in translated_chunks for line in chunk]
        return translated_text_list

    def translate_text_list(self, text_list):
        chunks = self._split_into_chunks(text_list)
        translated_chunks = self._translate_chunks(chunks)
        translated_text_list = self._reassemble_chunks(translated_chunks)
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

    def _translate_text(self, text):
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

    def _translate_text(self, text):
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

import os
class ManualTranslator(Translator):
    def __init__(self, api_key=None, target_lang='EN', max_chunk_size=5000):
        super().__init__(api_key, target_lang, max_chunk_size)
        self.file_path = "translation_input_output.txt"

    def _translate_text(self, text):
        """
        Receive the translated text from the user.

        :param text: The text to be translated
        :return: The translated text provided by the user
        """
        # Write the text to be translated to a file
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Inform the user to provide the translation
        print("Please provide the translation and press Enter.")

        # Wait for the user to finish providing the translation
        input()

        # Read the translated text from the same file
        with open(self.file_path, "r", encoding="utf-8") as f:
            translated_text = f.read()

        return translated_text

    def __del__(self):
        """
        Delete the file used for translation when the object is destroyed.
        """
        try:
            os.remove(self.file_path)
        except Exception as e:
            print(f"Error occurred while trying to remove file {self.file_path}: {e}")

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

class BrowserDeepLTranslator(Translator):
    def __init__(self, api_key=None, target_lang='EN', max_chunk_size=5000):
        """
        ブラウザを起動し、DeepLに翻訳対象のテキストを貼り付け、翻訳結果を刈り取ってリストにする。

        :param api_key: 未使用
        :param target_lang: 翻訳対象の言語コード（デフォルトは英語）
        :param max_chunk_size: 翻訳の分割上限文字数（デフォルトは5000）
        """
        super().__init__(api_key, target_lang, max_chunk_size)
        self.driver = webdriver.Chrome()  # or whichever browser driver you have

    def _translate_text(self, text):
        """
        ブラウザを操作してテキストをDeepLウェブサイトで翻訳します。

        :param text: 翻訳するテキスト
        :return: 翻訳後のテキスト
        """
        # Open DeepL website
        self.driver.get("https://www.deepl.com/translator")

        # Input the text to be translated
        input_area = self.driver.find_element_by_css_selector(".lmt__source_textarea")
        input_area.send_keys(text)

        # Wait for the translation to finish
        sleep(10)  # Adjust this value if your internet connection is slow

        # Scrape the translated text
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        translated_text = soup.select_one('.lmt__target_textarea').text

        return translated_text

class DataTranslator:
    def __init__(self, keys=None):
        """
        データトランスレータの初期化。

        :param keys: 翻訳するキーのリスト
        """
        self.keys = keys

import copy
class DataTranslator:
    def __init__(self, keys=None):
        self.keys = keys

    def _process_string(self, v, lines, is_parsing):
        if is_parsing:
            lines.append(v)
        else:
            return next(lines)

    def _process_list(self, data, key, lines, is_parsing):
        for i, item in enumerate(data):
            if isinstance(item, str) and (self.keys is None or key in self.keys):
                data[i] = self._process_string(item, lines, is_parsing)
            elif isinstance(item, (list, dict)):
                self._process_recursive(item, lines, is_parsing)

    def _process_dict(self, data, lines, is_parsing):
        for key, value in data.items():
            if isinstance(value, str) and (self.keys is None or key in self.keys):
                data[key] = self._process_string(value, lines, is_parsing)
            elif isinstance(value, list):
                self._process_list(value, key, lines, is_parsing)
            if isinstance(value, dict):
                self._process_recursive(value, lines, is_parsing)

    def _process_recursive(self, data, lines=None, is_parsing=False):
        if isinstance(data, dict):
            self._process_dict(data, lines, is_parsing)
        elif isinstance(data, list):
            self._process_list(data, None, lines, is_parsing)

    def parse_to_text(self, data):
        parsed_data = copy.deepcopy(data)
        lines = []
        self._process_recursive(parsed_data, lines, is_parsing=True)
        return lines

    def restore_from_text(self, original_data, lines):
        data = copy.deepcopy(original_data)
        lines_iter = iter(lines)
        self._process_recursive(data, lines_iter, is_parsing=False)
        return data

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
    parser = argparse.ArgumentParser(description="Translate a YAML file.")
    parser.add_argument("-i", "--input", default="sample.yaml", help="Input YAML file name.")
    parser.add_argument("-o", "--output", default="sample_en.yaml", help="Output YAML file name.")
    parser.add_argument("-l", "--language", default="JA", help="Target language for translation.")
    parser.add_argument("-m", "--max_chunk_size", default=5000, type=int, help="Maximum chunk size for translation.")
    parser.add_argument("-t", "--translator", choices=["deepl", "google", "manual", "browser"], default="deepl", help="Choice of translation method.")
    parser.add_argument("-k", "--keys", nargs="*", help="Keys to be translated. If not specified, all keys are translated.")

    args = parser.parse_known_args()[0]

    require_api_key = args.translator in ["deepl", "google"]
    parser.add_argument("-a", "--api_key", required=require_api_key, help="Translation API key.")

    args = parser.parse_args()

    return args

def create_translator(api_key, translator_type, max_chunk_size, language):
    translator_classes = {
        "deepl": DeepLTranslator,
        "google": GoogleTranslator,
        "manual": ManualTranslator,
        "browser": BrowserDeepLTranslator,
    }

    try:
        return translator_classes[translator_type](api_key, language, max_chunk_size=max_chunk_size)
    except KeyError:
        raise ValueError(f"Unknown translator type: {translator_type}")

def translate_file(input_file, output_file, api_key, translator_type, max_chunk_size, keys, language):
    translator = create_translator(api_key, translator_type, max_chunk_size, language)
    
    data_translator = DataTranslator(keys)
    yaml_handler = YamlHandler()

    # Load data from the input YAML file
    data = yaml_handler.load(input_file)

    # Convert the data to a list of texts
    text_list = data_translator.parse_to_text(data)

    # Translate the texts
    translated_text_list = translator.translate_text_list(text_list)

    # Restore the translated texts into the original data format
    output_data = data_translator.restore_from_text(data, translated_text_list)

    # Write the translated data to the output YAML file
    yaml_handler.dump(output_data, output_file)


if __name__ == "__main__":
    args = parse_arguments()
    translate_file(args.input, args.output, args.api_key, args.translator, args.max_chunk_size, args.keys, args.language)
