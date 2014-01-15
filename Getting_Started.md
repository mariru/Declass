Hop-a-thon
==========

Getting the data
----------------

Click [here](https://www.dropbox.com/sh/u3cwr4yunka6kuj/-3DXhDiHmj) to access the data on Dropbox.  Download what you want.

To extract the `.tar.bz2` files, 

    bzip2 -dc filename | tar -xf -

Installing VW
-------------
Follow the directions [here](https://github.com/JohnLangford/vowpal_wabbit/wiki/Tutorial), or follow the following steps:

### 1 Download 
[release 7.3](https://github.com/JohnLangford/vowpal_wabbit/archive/v7.3.tar.gz) and unpack it.

### Install boost

#### On Linux

```bash
sudo apt-get install libboost-program-options-dev
sudo apt-get install zlib1g-dev
```

#### On a mac

Download the source from [here](http://sourceforge.net/projects/boost/files/boost/1.50.0/)
Execute the shell script with `sudo ./bootstrap.sh`
Next run the command `sudo ./bjam --layout=tagged install`
Wait 15 minutes for it to install

### config/make/install vw

    cd vowpal_wabbit-7.3
    make
    make test
    make install


Start analyzing data
--------------------

Follow [this tutorial](https://github.com/declassengine/declass/blob/master/examples/vw_helpers.md)


About the data
--------------

All data stored at `mysql -u declass -p -h mysql.csail.mit.edu` in the database `declassification`.

* `cables-full` are the cables that were not withdrawn.  They are from the `statedeptcables` table.
* `cables-withdrawn` are those that were withdrawn.  They are from the `withdrawalcards` table.
