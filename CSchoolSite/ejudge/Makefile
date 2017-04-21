EJUDGEROOT = /home/ejudge/ejudge-src
INCLUDEDIR = "$(EJUDGEROOT)/include"
PYTHONCFG = python-config
SRC=src/ejudgemodule_ej36.c

CC = gcc
CFLAGS = -g -Wall -Wno-pointer-sign

PYTHONFLAGS = $(shell /usr/bin/env ${PYTHONCFG} --includes)
CBUILDFLAGS = -fPIC -DPIC -DPYTHON -D_GNU_SOURCE -std=gnu99

include files.make

libejudge/ejudgemodule.so : $(SRC) $(USERLIST_CLNT_MODULES)
	mkdir -p libejudge
	$(CC) -I $(INCLUDEDIR) -I $(EJUDGEROOT) $(CFLAGS) $(LDFLAGS) $(REUSE_INCL_OPT) $(PYTHONFLAGS) $(CBUILDFLAGS) -shared $^ -o $@
	cp src/libejudge.py libejudge/__init__.py

clean :
	-rm -rf libejudge
