from discovery.transcript import parse_vtt

def test_parse_vtt():
    vtt="""WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello <00:00:00.500>world\n\n00:00:02.000 --> 00:00:04.000\nHello world\n\n00:00:04.000 --> 00:00:06.000\nThis is new.\n"""
    r=parse_vtt(vtt); assert len(r)==2; assert r[0].text=="Hello world"; assert r[1].text=="This is new."
