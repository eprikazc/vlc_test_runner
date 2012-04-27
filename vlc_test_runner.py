import urllib
import os
import subprocess
import psutil
from matplotlib import pyplot

VLC_ARCHIVE_119 = "http://download.videolan.org/pub/videolan/vlc/1.1.9/vlc-1.1.9.tar.bz2"
VLC_ARCHIVE_200 = "http://download.videolan.org/pub/videolan/vlc/2.0.0/vlc-2.0.0.tar.xz"

TEST_MEDIA_FILE = "http://download.microsoft.com/download/6/8/f/68f212d7-f58d-4542-890d-65d7e790f2e0/The_Magic_of_Flight_720.exe"
PROJECT_DIR = os.path.join(os.path.expanduser("~"), "vlc_tests")
if not os.path.exists(PROJECT_DIR):
    os.mkdir(PROJECT_DIR)



def run_shell_command(*args, **kwargs):
    """
    Run specified shell command. Command and its arguments can be passed as positional arguments or as single list.
    Both following invocations are valid:
    run_shell_command("rm", "-rf", "note.txt")
    and
    run_shell_command(["rm", "-rf", "note.txt"])
    """
    if len(args) == 1 and isinstance(args[0], list):
        command = args[0]
    else:
        command = list(args)
    print "Running '%s'" %" ".join(command)

    subprocess.check_call(command, **kwargs)


def get_and_compile_vlc(vlc_archive_url, target_directory, code_coverage = False):
    file_name = vlc_archive_url.split('/')[-1]
    extension = file_name.split(".")[-1]
    vlc_directory = file_name.split(".tar")[0]

    os.chdir(PROJECT_DIR)
    if not os.path.exists(target_directory):
        os.mkdir(target_directory)
    if not os.path.exists(file_name):
        print "Downloading vlc archive"
        run_shell_command("wget", vlc_archive_url)
    if extension == "xz":
        tar_flags = "xfJ"
    elif extension == "bz2":
        tar_flags = "xfj"
    else:
        raise Exception, "Unsupported archive extension: %s" %extension
    print "Descompressing vlc source archive"
    run_shell_command("tar", tar_flags, file_name, "-C", target_directory)

    os.chdir(os.path.join(target_directory, vlc_directory))
    configure_command = ["sudo", "./configure", "--enable-x11", "--enable-xvideo", "--enable-sdl", "--enable-avcodec", "--enable-avformat",
 "--enable-swscale", "--enable-mad", "--enable-libdvbpsi", "--enable-a52", "--enable-libmpeg2", "--enable-dvdnav",
 "--enable-faad", "--enable-vorbis", "--enable-ogg", "--enable-theora", "--enable-faac", "--enable-mkv", "--enable-freetype",
 "--enable-fribidi", "--enable-speex", "--enable-flac", "--disable-live555", "--with-live555-tree=/usr/lib/live",
 "--enable-caca", "--enable-skins", "--enable-skins2", "--enable-alsa", "--enable-qt4", "--enable-ncurses"]
    if code_coverage:
        configure_command.append("CFLAGS=-fprofile-arcs -ftest-coverage")
    run_shell_command(configure_command)
    run_shell_command("sudo", "make")
    return os.path.join(PROJECT_DIR, target_directory, vlc_directory)


def play_file_and_capture_os_stat(vlc_directory, test_media_file_name):
    cpu_data = []
    memory_data = []

    p = subprocess.Popen(["./vlc", "--vout", "x11", "--play-and-exit", test_media_file_name], cwd=vlc_directory)
    while p.poll() is None:
        memory_data.append(psutil.phymem_usage().used)
        cpu_data.append(psutil.cpu_percent(1))
    return {"cpu_data": cpu_data, "memory_data": memory_data}


def play_file_and_get_coverage_report(vlc_directory, test_media_file_name):
    os.chdir(vlc_directory)
    run_shell_command("./vlc", "--vout", "x11", "--play-and-exit", os.path.join(PROJECT_DIR, test_media_file_name))
    run_shell_command("lcov", "--directory", vlc_directory, "-c", "--output-file", "coverage.info")
    run_shell_command("genhtml", "coverage.info")


def play_file_under_valgrind(vlc_directory, test_media_file_name):
    os.chdir(vlc_directory)
    valgrind_log_file = open("valgrind.log", "a")
    run_shell_command("valgrind", "--leak-check=yes", "./vlc", "--vout", "x11", "--play-and-exit", os.path.join(PROJECT_DIR, test_media_file_name),
        stdout=valgrind_log_file, stderr=valgrind_log_file)


def run():
    vlc_119_dir = vlc_200_dir = None
    os.chdir(PROJECT_DIR)
    test_media_archive = TEST_MEDIA_FILE.split("/")[-1]
    test_media_file_name = test_media_archive.replace(".exe", ".wmv")
    if not os.path.exists(test_media_archive):
        print "Downloading test media file"
        run_shell_command("wget", TEST_MEDIA_FILE)
        print "test media file downloaded. Extracting it."
    if not os.path.exists(test_media_file_name):
        run_shell_command("unzip", test_media_archive)

    print "Installing build dependencies for vlc"
    run_shell_command("sudo", "apt-get", "build-dep", "vlc", "-y")
    run_shell_command("sudo", "apt-get", "install", "-y", "libxcb-shm0-dev", "libxcb-xv0-dev", "libxcb-keysyms1-dev",
        "libxcb-randr0-dev", "libxcb-composite0-dev", "lcov", "valgrind")
    regular_test_dir = "regular_test"
    code_coverage_dir = "code_coverage_test"
    vlc_119_dir = get_and_compile_vlc(VLC_ARCHIVE_119, regular_test_dir)
    vlc_200_dir = get_and_compile_vlc(VLC_ARCHIVE_200, regular_test_dir)
    vlc_119_stat = play_file_and_capture_os_stat(vlc_119_dir, os.path.join(PROJECT_DIR, test_media_file_name))
    vlc_200_stat = play_file_and_capture_os_stat(vlc_200_dir, os.path.join(PROJECT_DIR, test_media_file_name))
    pyplot.figure("CPU usage")
    pyplot.plot(vlc_119_stat["cpu_data"], label="vlc_1.x")
    pyplot.plot(vlc_200_stat["cpu_data"], label="vlc_2.0")
    pyplot.legend()
    cpu_usage_png = os.path.join(PROJECT_DIR, regular_test_dir, "cpu_usage.png")
    print "Saving plot to %s" %cpu_usage_png
    pyplot.savefig(cpu_usage_png)
    pyplot.figure("Memory usage")
    pyplot.plot(vlc_119_stat["memory_data"], label="vlc_1.x")
    pyplot.plot(vlc_200_stat["memory_data"], label="vlc_2.0")
    pyplot.legend()
    mem_usage_png = os.path.join(PROJECT_DIR, regular_test_dir, "mem_usage.png")
    print "Saving plot to %s" %mem_usage_png
    pyplot.savefig(mem_usage_png)

    vlc_119_cc_dir = get_and_compile_vlc(VLC_ARCHIVE_119, code_coverage_dir, True)
    vlc_200_cc_dir = get_and_compile_vlc(VLC_ARCHIVE_200, code_coverage_dir, True)
    play_file_and_get_coverage_report(vlc_119_cc_dir, test_media_file_name)
    play_file_and_get_coverage_report(vlc_200_cc_dir, test_media_file_name)


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
