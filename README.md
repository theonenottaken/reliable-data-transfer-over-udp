# reliable-data-transfer-over-udp

For a summary and explanation of the project, please see the assignment specifications file as well as the report file. This README will explain how to run the program.

#### How to Run

You will be able to run the program on either a Linux system or a Windows system. Running on Windows, however, requires cygwin. If you don't have cygwin, it will be easier to use Linux,
but if you must, here's a link to help install cygwin on Windows: http://merlot.usc.edu/cs353-s18/cygwin/

The instructions differ slightly whether you're using Windows or Linux, which I will explain.

Download the repository so that all the files reside in a single directory on your computer. One of the folders within this directory is called RELAY. Open a command prompt (or terminal)
and `cd` to the RELAY folder.

Now, if you're on Linux, enter this command: `./udp_64.out 10000 10 1 1 20 10 1`

And if you're on Windows, enter this command: `udp_64_cygwin.exe 1000 10 1 1 20 10 1`

What have we just done is we have started the RELAY program, which will relay data between Homeland and Embassy (if you don't know what I'm talking about, check out the other PDF files
from this repository). Also check out the second page of the assignment specifications file for more of an explanation of the RELAY program and particularly what all of these parameters are.
The numbers I've offered are merely a suggestion. You can fiddle with the parameters all you want (except for the 10000. That's the port number and RELAY will only work with that number).

Now, it's time to run Embassy. `cd` to the directory containing embassy.py (probably the original directory that the repository was downloaded into) and enter the following command:
`python embassy.py 127.0.0.1`. The four numbers separated by periods here is the IP address of the RELAY program. I assume you're running all of the programs on the same machine, so
127.0.0.1 is what you use.

Next, Homeland. Enter this command: `python homeland.py 127.0.0.1`. Again, the parameter is the IP address of RELAY.

That's it. Notice that there is file in the directory called "input.txt". After the programs finish, you should see another file here called "output.txt.". The two files should be
exactly identical. You can compare them using file comparing tools.