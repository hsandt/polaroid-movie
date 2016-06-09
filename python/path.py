import os
PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))


def get_full_path(*path):
    return os.path.join(PROJECT_DIRECTORY, *path)

def get_video_path(*path):
    return os.path.join(PROJECT_DIRECTORY, 'videos', *path)
