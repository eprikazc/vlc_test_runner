import urllib
import os
import subprocess

vlc_archive_117 = "http://download.videolan.org/pub/videolan/vlc/1.1.7/vlc-1.1.7.tar.bz2"
vlc_archive_119 = "http://download.videolan.org/pub/videolan/vlc/1.1.9/vlc-1.1.9.tar.bz2"
vlc_archive_200 = "http://download.videolan.org/pub/videolan/vlc/2.0.0/vlc-2.0.0.tar.xz"


def run_shell_command(*args):
    command = list(args)
    print "Running '%s'" %" ".join(command)
    subprocess.call(command)


def get_and_compile_vlc(vlc_archive_url):
    os.chdir(os.path.expanduser("~"))
    run_shell_command("wget", vlc_archive_url)
    file_name = vlc_archive_url.split('/')[-1]
    extension = file_name.split(".")[-1]
    if extension == "xz":
        tar_flags = "xfJ"
    elif extension == "bz2":
        tar_flags = "xfj"
    else:
        raise Exception, "Unsupported archive extension: %s" %extension
    print "Descompressing vlc source archive"
    run_shell_command("tar", tar_flags, file_name)
    vlc_directory = file_name.split(".tar")[0]
    os.chdir(vlc_directory)
    run_shell_command("./configure", "--enable-x11", "--enable-xvideo", "--enable-sdl", "--enable-avcodec", "--enable-avformat",
 "--enable-swscale", "--enable-mad", "--enable-libdvbpsi", "--enable-a52", "--enable-libmpeg2", "--enable-dvdnav",
 "--enable-faad", "--enable-vorbis", "--enable-ogg", "--enable-theora", "--enable-faac", "--enable-mkv", "--enable-freetype",
 "--enable-fribidi", "--enable-speex", "--enable-flac", "--enable-live555", "--with-live555-tree=/usr/lib/live",
 "--enable-caca", "--enable-skins", "--enable-skins2", "--enable-alsa", "--enable-qt4", "--enable-ncurses")
    run_shell_command("make")
    run_shell_command("make", "clean")

def run():
    run_shell_command("apt-get", "build-dep", "vlc")
    get_and_compile_vlc(vlc_archive_119)


if __name__ == '__main__':
    run()
