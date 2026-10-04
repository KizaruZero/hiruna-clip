from discovery.timecode import seconds_to_timecode,timecode_to_seconds

def test_timecode():
    assert seconds_to_timecode(65.4)=="00:01:05"
    assert seconds_to_timecode(3661.7)=="01:01:02"
    assert timecode_to_seconds("01:02:03.5")==3723.5
