import urllib
import os
import subprocess
import psutil
from matplotlib import pyplot

VLC_ARCHIVE_119 = "http://download.videolan.org/pub/videolan/vlc/1.1.9/vlc-1.1.9.tar.bz2"
VLC_ARCHIVE_200 = "http://download.videolan.org/pub/videolan/vlc/2.0.0/vlc-2.0.0.tar.xz"

TEST_MEDIA_FILE = "http://download.microsoft.com/download/6/8/f/68f212d7-f58d-4542-890d-65d7e790f2e0/The_Magic_of_Flight_720.exe"


def run_shell_command(*args):
    command = list(args)
    print "Running '%s'" %" ".join(command)
    subprocess.check_call(command)


def get_and_compile_vlc(vlc_archive_url):
    file_name = vlc_archive_url.split('/')[-1]
    extension = file_name.split(".")[-1]
    vlc_directory = file_name.split(".tar")[0]

    os.chdir(os.path.expanduser("~"))
    run_shell_command("wget", vlc_archive_url)
    if extension == "xz":
        tar_flags = "xfJ"
    elif extension == "bz2":
        tar_flags = "xfj"
    else:
        raise Exception, "Unsupported archive extension: %s" %extension
    print "Descompressing vlc source archive"
    run_shell_command("tar", tar_flags, file_name)
    run_shell_command("rm", file_name)
    try:
        os.chdir(vlc_directory)
        run_shell_command("sudo", "./configure", "--enable-x11", "--enable-xvideo", "--enable-sdl", "--enable-avcodec", "--enable-avformat",
     "--enable-swscale", "--enable-mad", "--enable-libdvbpsi", "--enable-a52", "--enable-libmpeg2", "--enable-dvdnav",
     "--enable-faad", "--enable-vorbis", "--enable-ogg", "--enable-theora", "--enable-faac", "--enable-mkv", "--enable-freetype",
     "--enable-fribidi", "--enable-speex", "--enable-flac", "--disable-live555", "--with-live555-tree=/usr/lib/live",
     "--enable-caca", "--enable-skins", "--enable-skins2", "--enable-alsa", "--enable-qt4", "--enable-ncurses")
        run_shell_command("sudo", "make")
    except Exception:
        os.chdir(os.path.expanduser("~"))
        run_shell_command("sudo", "rm", "-rf", vlc_directory)
        raise
    return os.path.join(os.path.expanduser("~"), vlc_directory)


def play_file_and_capture_os_stat(vlc_directory, test_media_file_name):
    cpu_data = []
    memory_data = []

    p = subprocess.Popen(["./vlc", "--vout", "x11", "--play-and-exit", test_media_file_name], cwd=vlc_directory)
    while p.poll() is None:
        memory_data.append(psutil.phymem_usage().used)
        cpu_data.append(psutil.cpu_percent(1))
    return {"cpu_data": cpu_data, "memory_data": memory_data}


def run():
    vlc_119_dir = vlc_200_dir = None
    os.chdir(os.path.expanduser("~"))
    test_media_archive = TEST_MEDIA_FILE.split("/")[-1]
    test_media_file_name = test_media_archive.replace(".exe", ".wmv")
    if not os.path.exists(test_media_archive):
        print "Downloading test media file"
        run_shell_command("wget", TEST_MEDIA_FILE)
        print "test media file downloaded. Extracting it."
    if not os.path.exists(test_media_file_name):
        run_shell_command("unzip", test_media_file_archive)

    print "Installing build dependencies for vlc"
    run_shell_command("sudo", "apt-get", "build-dep", "vlc", "-y")
    run_shell_command("sudo", "apt-get", "install", "-y", "libxcb-shm0-dev", "libxcb-xv0-dev", "libxcb-keysyms1-dev",
        "libxcb-randr0-dev", "libxcb-composite0-dev")
    try:
        vlc_119_dir = get_and_compile_vlc(VLC_ARCHIVE_119)
        vlc_200_dir = get_and_compile_vlc(VLC_ARCHIVE_200)
        vlc_119_stat = play_file_and_capture_os_stat(vlc_119_dir, os.path.join(os.path.expanduser("~"), test_media_file_name))
        vlc_200_stat = play_file_and_capture_os_stat(vlc_200_dir, os.path.join(os.path.expanduser("~"), test_media_file_name))
        pyplot.figure("CPU usage")
        pyplot.plot(vlc_119_stat["cpu_data"], label="vlc_1.x")
        pyplot.plot(vlc_200_stat["cpu_data"], label="vlc_2.0")
        pyplot.legend()
        cpu_usage_png = os.path.join(os.path.expanduser("~"), "cpu_usage.png")
        print "Saving plot to %s" %cpu_usage_png
        pyplot.savefig(cpu_usage_png)
        pyplot.figure("Memory usage")
        pyplot.plot(vlc_119_stat["memory_data"], label="vlc_1.x")
        pyplot.plot(vlc_200_stat["memory_data"], label="vlc_2.0")
        pyplot.legend()
        mem_usage_png = os.path.join(os.path.expanduser("~"), "mem_usage.png")
        print "Saving plot to %s" %mem_usage_png
        pyplot.savefig(mem_usage_png)
        pyplot.show()
    finally:
        print "Cleaning up"
        if vlc_119_dir:
            run_shell_command("sudo", "rm", "-rf", vlc_119_dir)
        if vlc_200_dir:
            run_shell_command("sudo", "rm", "-rf", vlc_200_dir)


if __name__ == '__main__':
    run()
    '''
    vlc_data_1 = play_file_and_capture_os_stat('/home/eugene/vlc-1.1.9/', '/home/eugene/The_Magic_of_Flight_720.wmv')
    vlc_data_2 = play_file_and_capture_os_stat('/home/eugene/vlc-2.0.0/', '/home/eugene/The_Magic_of_Flight_720.wmv')

    pyplot.figure("CPU usage")
    pyplot.plot(vlc_data_1["cpu_data"], label="vlc_1.x")
    pyplot.plot(vlc_data_2["cpu_data"], label="vlc_2.0")
    pyplot.legend()
    pyplot.figure("Memory usage")
    pyplot.plot(vlc_data_1["memory_data"], label="vlc_1.x")
    pyplot.plot(vlc_data_2["memory_data"], label="vlc_2.0")
    pyplot.legend()
    print len(vlc_data_1["memory_data"])
    print len(vlc_data_2["memory_data"])

    pyplot.show()
    '''
