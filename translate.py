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
                translated_chunk = self._translate_text('\n'.join(chunk))
                translated_text_list.extend(translated_chunk.split('\n'))
                chunk = [text]
                chunk_size = text_len

        if chunk:
            translated_chunk = self._translate_text('\n'.join(chunk))
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

    def _translate_text(self, text):
        print(text)
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
        print(response.json())
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

import sys
class ManualTranslator(Translator):
    def __init__(self, api_key=None, target_lang='EN', max_chunk_size=5000):
        """
        手動翻訳クラス。

        :param api_key: 未使用
        :param target_lang: 翻訳対象の言語コード（デフォルトは英語）
        :param max_chunk_size: 翻訳の分割上限文字数（デフォルトは5000）
        """
        super().__init__(api_key, target_lang, max_chunk_size)

    def _translate_text(self, text):
        """
        ユーザーによる手動翻訳のためのプロンプトを表示します。

        :param text: 翻訳するテキスト
        :return: ユーザーが入力した翻訳テキスト
        """
        raise NotImplementedError("This method is not intended to be used in ManualTranslator.")

    def translate_text_list(self, text_list):
        """
        テキストのリストを翻訳します。

        テキストは`self.max_chunk_size`を超えないようにチャンク化されます。
        翻訳後、翻訳テキストは単一の文字列として返されます。

        :param text_list: 翻訳するテキストのリスト
        :return: 翻訳テキストのリスト
        """

        # テキストのチャンク化の準備
        chunk = []  # 現在のテキストチャンク
        chunk_size = 0  # 現在のチャンクサイズ

        # すべてのテキストチャンクを保存
        chunks = []

        # 各テキストを処理
        for text in text_list:
            text_len = len(text)

            # 現在のテキストがチャンクに収まる場合、追加する
            if chunk_size + text_len <= self.max_chunk_size:
                chunk.append(text)
                chunk_size += text_len
            # それ以外の場合、現在のチャンクを確定し、新しいチャンクを開始する
            else:
                chunks.append('\n'.join(chunk))
                chunk = [text]
                chunk_size = text_len

        # 最後のチャンクを確定
        if chunk:
            chunks.append('\n'.join(chunk))

        # チャンクを出力し、翻訳を収集し、それを返す
        print('\n'.join(chunks))
        
        translated_text_list = []
        for line in sys.stdin:
            line = line.rstrip('\n')
            if line: 
                translated_text_list.append(line)

        return translated_text_list

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

class DataTranslator:
    def __init__(self, keys=None):
        self.keys = keys

    def _parse_to_text_recursive(self, data, lines):
        if isinstance(data, dict):
            for k, v in data.items():
                if self.keys is None or k in self.keys:
                    if isinstance(v, str):
                        lines.append(v)
                    elif isinstance(v, list):
                        lines.extend(item for item in v if isinstance(item, str))
                else:
                    self._parse_to_text_recursive(v, lines)
        elif isinstance(data, list):
            for item in data:
                self._parse_to_text_recursive(item, lines)

    def parse_to_text(self, data):
        lines = []
        self._parse_to_text_recursive(data, lines)
        return lines

    def restore_from_text(self, data, lines):
        lines_iter = iter(lines)
        self._restore_from_text_recursive(data, lines_iter)

    def _restore_from_text_recursive(self, data, lines_iter):
        if isinstance(data, dict):
            for k, v in data.items():
                if self.keys is None or k in self.keys:
                    if isinstance(v, str):
                        data[k] = next(lines_iter)
                    elif isinstance(v, list):
                        for i in range(len(v)):
                            if isinstance(v[i], str):
                                v[i] = next(lines_iter)
                else:
                    self._restore_from_text_recursive(v, lines_iter)
        elif isinstance(data, list):
            for item in data:
                self._restore_from_text_recursive(item, lines_iter)

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

    args.keys = None if args.keys == ['*'] else args.keys
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
    data_translator.restore_from_text(data, translated_text_list)

    # Write the translated data to the output YAML file
    yaml_handler.dump(data, output_file)


if __name__ == "__main__":
    args = parse_arguments()
    translate_file(args.input, args.output, args.api_key, args.translator, args.max_chunk_size, args.keys, args.language)
