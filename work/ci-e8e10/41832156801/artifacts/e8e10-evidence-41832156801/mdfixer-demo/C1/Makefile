CC      = gcc
CFLAGS  = -I.

main: main.o
	$(CC) -o $@ $^

main.o: main.c config.h
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: check clean
check: main
	./main

clean:
	rm -f main.o main main.d
