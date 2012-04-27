vlc_test_runner
===============
Prerequisite steps:

0. Prepare target OS - Ubuntu 11.04

1. Run "sudo apt-get build-dep matplotlib"

2. Install Python dependencies from requirements.txt: "sudo easy_install pip; sudo pip install -r requirements.txt"

3. Script executes a few commands via 'sudo'. So, you should have sudo configured. And (depending on your sudo configuration) you should be ready to enter password if requested.

4. By default script stores all its data (test video file, vlc source code archives, compiled vlc code, test results) to "~/vlc_tests" folder. At the moment the folder is not cleaned. You should clean the folder between script runs by yourself.
