CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2

all: hello

hello: main.c
	$(CC) $(CFLAGS) -o hello main.c

clean:
	rm -f hello

.PHONY: all clean
