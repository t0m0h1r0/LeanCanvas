import requests
from ruamel.yaml import YAML
import argparse

# DeepLのAPIを使ってテキストを翻訳するクラス
class DeepLTranslator:
    def __init__(self, api_key, target_lang='EN'):
        self.api_key = api_key
        self.url = "https://api-free.deepl.com/v2/translate"
        self.target_lang = target_lang  # 翻訳対象の言語

    # テキストを翻訳するメソッド
    def translate(self, text):
        response = requests.post(
            self.url,
            data={
                'auth_key': self.api_key,
                'text': text,
                'target_lang': self.target_lang,  # 翻訳対象の言語を指定
            },
        )
        return response.json()["translations"][0]["text"]

    # 複数のテキストを翻訳するメソッド
    # テキストが5000文字を超える場合は、その前までのテキストを一度に翻訳し、翻訳後のテキストをリストに追加する
    # テキストが5000文字を超えない場合は、テキストをチャンクに追加し、チャンクのサイズを更新する
    # チャンクが空でない場合は、残ったテキストを翻訳し、翻訳後のテキストをリストに追加する
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

# データを翻訳用のテキストに変換したり、逆に翻訳後のテキストを元のデータ形式に戻すクラス
class DataTranslator:
    # 入力として受け取ったデータをテキスト形式に変換するメソッド
    def parse_to_text(self, data):
        lines = []  # テキストの各行を保存するリスト
        self._parse_to_text_recursive(data, lines)  # 再帰的な処理を行う
        return lines

    # データをテキストに再帰的に変換する内部メソッド
    def _parse_to_text_recursive(self, data, lines):
        if isinstance(data, dict):  # データが辞書型の場合
            for v in data.values():
                self._parse_to_text_recursive(v, lines)
        elif isinstance(data, list):  # データがリスト型の場合
            for v in data:
                self._parse_to_text_recursive(v, lines)
        elif isinstance(data, str):  # データが文字列型の場合
            lines.append(data)

    # 入力として受け取ったデータに翻訳後のテキストを適用するメソッド
    def restore_from_text(self, data, translated_lines):
        self._restore_from_text_recursive(data, iter(translated_lines))  # 再帰的な処理を行う

    # データに翻訳後のテキストを再帰的に適用する内部メソッド
    def _restore_from_text_recursive(self, data, translated_lines):
        if isinstance(data, dict):  # データが辞書型の場合
            for k, v in data.items():
                if isinstance(v, str):  # 値が文字列型の場合
                    data[k] = next(translated_lines)  # 翻訳後のテキストを適用する
                else:
                    self._restore_from_text_recursive(v, translated_lines)
        elif isinstance(data, list):  # データがリスト型の場合
            for i in range(len(data)):
                if isinstance(data[i], str):  # 値が文字列型の場合
                    data[i] = next(translated_lines)  # 翻訳後のテキストを適用する
                else:
                    self._restore_from_text_recursive(data[i], translated_lines)

# YAML形式のデータの読み書きを行うクラス
class YamlHandler:
    def __init__(self):
        self.yaml = YAML()

    def load(self, filename):
        with open(filename) as file:
            return self.yaml.load(file)

    def dump(self, data, filename):
        with open(filename, 'w') as file:
            self.yaml.dump(data, file)

# コマンドライン引数を解析する関数
def parse_arguments():
    parser = argparse.ArgumentParser(description="Translate a YAML file using the DeepL API.")
    parser.add_argument("--input", default="sample.yaml", help="Input YAML file name.")
    parser.add_argument("--output", default="sample_en.yaml", help="Output YAML file name.")
    parser.add_argument("--api_key", required=True, help="DeepL API key.")
    args = parser.parse_args()
    return args

# 入力ファイルを翻訳して出力ファイルに保存する関数
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
