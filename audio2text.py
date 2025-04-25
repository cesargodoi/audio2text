import math
import os
import shutil
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment


class Audio2Text:
    def __init__(self, input_path):
        self.input_path = input_path
        self.audio_name = str(input_path).split("/")[-1].split(".")[0]
        self.chunk_length_ms = 30_000
        self.chunk_paths = self.split_audio()
        self.full_text = ""

    def split_audio(self):
        audio = AudioSegment.from_file(self.input_path)
        total_length = len(audio)

        output_folder = f"audios/chunks/{self.audio_name}"
        os.makedirs(output_folder, exist_ok=True)

        num_chunks = math.ceil(total_length / self.chunk_length_ms)
        chunk_paths = []

        for i in range(num_chunks):
            start = i * self.chunk_length_ms
            end = min(start + self.chunk_length_ms, total_length)
            chunk = audio[start:end]
            chunk_path = os.path.join(output_folder, f"chunk_{i:03d}.wav")
            chunk.export(chunk_path, format="wav")
            chunk_paths.append(chunk_path)

        return chunk_paths

    def transcribe(self):
        recognizer = sr.Recognizer()

        print(f"- {self.audio_name} ", end="", flush=True)

        for path in self.chunk_paths:
            print(".", end="", flush=True)

            with sr.AudioFile(path) as source:
                audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language="pt-BR")
                self.full_text += text + " "
            except sr.UnknownValueError:
                self.full_text += "[inaudível] "
            except sr.RequestError as e:
                self.full_text += f"[erro: {e}] "

        print()
        return self.full_text

    def write_to_file(self, text_file_path):
        with open(text_file_path, "a") as f:
            f.write(f"{self.full_text}\n\n")


def main():
    print(" AUDIO TO TEXT ".center(80, "-"))
    text_file_name = input("Enter the name of the text file: ")
    text_file_path = Path(f"texts/{text_file_name}.txt")
    text_file_path.touch(exist_ok=True)

    audio_folder = "audios"
    audio_files = [
        file
        for file in os.listdir(audio_folder)
        if os.path.isfile(os.path.join(audio_folder, file))
    ]

    for file in audio_files:
        text = Audio2Text(f"{audio_folder}/{file}")
        text.transcribe()
        text.write_to_file(str(text_file_path))

    shutil.rmtree("audios/chunks")

    print(
        "The transcription was made for the file: '{}.txt'".format(
            text_file_name
        )
    )
    print("Bye!")


if __name__ == "__main__":
    main()
