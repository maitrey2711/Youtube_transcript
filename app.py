from distutils.log import debug
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, VideoUnavailable, TooManyRequests, TranscriptsDisabled, NoTranscriptAvailable
from youtube_transcript_api.formatters import TextFormatter

import nltk

import os

from summarizer import  nltk_summarize 


def create_app():
    # Creating Flask Object and returning it.
    app = Flask(__name__)

    # "Punkt" download before nltk tokenization
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print('Downloading punkt')
        nltk.download('punkt', quiet=True)

    # "Wordnet" download before nltk tokenization
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print('Downloading wordnet')
        nltk.download('wordnet')

    # "Stopwords" download before nltk tokenization
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print('Downloading Stopwords')
        nltk.download("stopwords", quiet=True)

    # Processing Function for below route.
    @app.route('/summarize/', methods=['GET'])
    def transcript_fetched_query():
        # Getting argument from the request
        video_id = request.args.get('id')  # video_id of the YouTube Video

        # Checking whether all parameters exist or not
        if video_id :
            # Every parameter exists here: checking validity of choice
            try:
                # Using Formatter to store and format received subtitles properly.
                formatter = TextFormatter()
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                formatted_text = formatter.format_transcript(transcript).replace("\n", " ")

                # Checking the length of sentences in formatted_text string, before summarizing it.
                num_sent_text = len(nltk.sent_tokenize(formatted_text))

                # Pre-check if the summary will have at least one line .
                select_length = int(num_sent_text * (int(50) / 100))

                # Summary will have at least 1 line. Proceed to summarize.
                if select_length > 0:

                    # Condition satisfied for summarization, summarizing the formatted_text based on choice.
                    if num_sent_text > 1:

                        # Summarizing Formatted Text based upon the request's choice
                        summary = nltk_summarize(formatted_text,50)  # Spacy Library for frequency-based summary.
                        
                        # Checking the length of sentences in summary string.
                        num_sent_summary = len(nltk.sent_tokenize(summary))

                        # Returning Result
                        response_list = {
                            # 'fetched_transcript': formatted_text,
                            'processed_summary': summary,
                            'length_original': len(formatted_text),
                            'length_summary': len(summary),
                            'sentence_original': num_sent_text,
                            'sentence_summary': num_sent_summary
                        }

                        return jsonify(success=True,
                                        message="Subtitles for this video was fetched and summarized successfully.",
                                        response=response_list), 200

                    else:
                        return jsonify(success=False,
                                        message="Subtitles are not formatted properly for this video. Unable to "
                                                "summarize. There is a possibility that there is no punctuation in "
                                                "subtitles of your video.",
                                        response=None), 400

                else:
                    return jsonify(success=False,
                                    message="Number of lines in the subtitles of your video is not "
                                            "enough to generate a summary. Number of sentences in your video: {}"
                                    .format(num_sent_text),
                                    response=None), 400

            # Catching Exceptions
            except VideoUnavailable:
                return jsonify(success=False, message="VideoUnavailable: The video is no longer available.",
                                response=None), 400
            except TooManyRequests:
                return jsonify(success=False,
                                message="TooManyRequests: YouTube is receiving too many requests from this IP."
                                        " Wait until the ban on server has been lifted.",
                                response=None), 500
            except TranscriptsDisabled:
                return jsonify(success=False, message="TranscriptsDisabled: Subtitles are disabled for this video.",
                                response=None), 400
            except NoTranscriptAvailable:
                return jsonify(success=False,
                                message="NoTranscriptAvailable: No transcripts are available for this video.",
                                response=None), 400
            except NoTranscriptFound:
                return jsonify(success=False, message="NoTranscriptAvailable: No transcripts were found.",
                                response=None), 400
            except:
                # Prevent server error by returning this message to all other un-expected errors.
                return jsonify(success=False,
                                message="Some error occurred."
                                        " Contact the administrator if it is happening too frequently.",
                                response=None), 500
        elif video_id is None or len(video_id) <= 0:
            # video_id parameter doesn't exist in the request.
            return jsonify(success=False,
                           message="Video ID is not present in the request. "
                                   "Please check that you have added id in your request correctly.",
                           response=None), 400
        else:
            # Some another edge case happened. Return this message for preventing exception throw.
            return jsonify(success=False,
                           message="Please request the server with your arguments correctly.",
                           response=None), 400

    @app.route('/')
    def summarizer_web():
        # We are at web.html, online input boxes are there to summarize the given video URL.
        # Displaying web.html to the end user
        return render_template('web.html')

    return app


if __name__ == '__main__':
    # Running Flask Application 
    # app.run()
    flask_app = create_app()
    flask_app.run(debug=True)
    