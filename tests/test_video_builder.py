from news_shorts import video_builder as vb


class DummyClip:
    def __init__(self, *args, **kwargs):
        self.duration = 1
        self.h = 10
    def set_fps(self, fps):
        return self
    def resize(self, size):
        return self
    def set_audio(self, a):
        return self
    def set_position(self, pos):
        return self
    def set_duration(self, d):
        self.duration = d
        return self
    def write_videofile(self, path, **kwargs):
        with open(path, 'wb') as f:
            f.write(b'')
        return path


def dummy_audio(text, path):
    with open(path, 'wb') as f:
        f.write(b'0')


def test_build_video_creates_file(tmp_path, monkeypatch):
    out = tmp_path / 'out.mp4'
    monkeypatch.setattr(vb, 'generate_audio', dummy_audio)
    monkeypatch.setattr(vb, 'AudioFileClip', lambda p: DummyClip())
    monkeypatch.setattr(vb, 'ImageClip', lambda *a, **k: DummyClip())
    monkeypatch.setattr(vb, 'TextClip', lambda *a, **k: DummyClip())
    monkeypatch.setattr(vb, 'CompositeVideoClip', lambda clips: DummyClip())
    monkeypatch.setattr(vb, 'concatenate_videoclips', lambda clips, method='compose': DummyClip())
    vb.build_video(['hello'], video_path=str(out), audio_dir=str(tmp_path))
    assert out.exists()

