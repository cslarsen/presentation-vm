CFLAGS = -O3 -march=native -mtune=native
TARGETS := bfl
LDFLAGS = -llightning

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
