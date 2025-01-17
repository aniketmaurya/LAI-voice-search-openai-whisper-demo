# class to set up whisper model
# predict method:
#   1. does the audio transcription to english text
#   2. return the search results for ddg in html format to serve to gradio
import whisper

from .ddg_search_component import Search


class WhisperSearch:
    def _setup(self):
        self.model = whisper.load_model("base")

    def __init__(self):
        self.model = None
        self.web_crawler = Search()

        self._setup()

    def _prep_audio(self, audio_file_path):
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(audio_file_path)
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        return mel

    def _detect_spoken_language(self, mel):
        _, probs = self.model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        return max(probs, key=probs.get)

    def predict(self, audio_file_path):
        # get the mel spectrogram
        mel = self._prep_audio(audio_file_path)

        # get the language
        # language = self._detect_spoken_language(mel)

        # do the transcription - uncomment one of the options line as per env
        options = whisper.DecodingOptions(
            task="translate", fp16=False
        )  # for running on CPU
        # options = whisper.DecodingOptions(task='translate') # for running on GPU
        result = whisper.decode(self.model, mel, options)

        return result.text

    def get_search_results_from_speech(self, audio_file_path):
        search_query = self.predict(audio_file_path=audio_file_path)

        search_results = self.web_crawler.search(search_query)

        return search_results
