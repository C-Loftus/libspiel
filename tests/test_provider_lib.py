import unittest, os
import gi

gi.require_version("SpielProvider", "0.1")
from gi.repository import SpielProvider

from _common import test_main


class TestSpeak(unittest.TestCase):
    def test_bad_header(self):
        r, w = os.pipe2(os.O_NONBLOCK)

        sr = SpielProvider.StreamReader.new(r)

        ww = os.fdopen(w, "w")
        ww.write("boop")

        success = sr.get_stream_header()
        self.assertFalse(success)

    def test_simple(self):
        r, w = os.pipe2(os.O_NONBLOCK)

        sw = SpielProvider.StreamWriter.new(w)
        sr = SpielProvider.StreamReader.new(r)

        sw.send_stream_header()
        sw.send_audio(b"foo")
        sw.send_event(2, 20, 24, "bar")

        success = sr.get_stream_header()
        self.assertTrue(success)

        # Event is not next chunk, so return empty event
        event_type, range_start, range_end, mark_name = sr.get_event()
        self.assertEqual(event_type, SpielProvider.EventType.NONE)
        self.assertEqual(range_start, 0)
        self.assertEqual(range_end, 0)
        self.assertEqual(mark_name, None)

        # Get audio chunk
        audio = sr.get_audio()
        self.assertEqual(audio, b"foo")

        # Audio is not next chunk, return empty buffer
        audio = sr.get_audio()
        self.assertEqual(audio, b"")

        # Get event chunk
        event_type, range_start, range_end, mark_name = sr.get_event()
        self.assertEqual(event_type, SpielProvider.EventType.SENTENCE)
        self.assertEqual(range_start, 20)
        self.assertEqual(range_end, 24)
        self.assertEqual(mark_name, "bar")


if __name__ == "__main__":
    test_main()