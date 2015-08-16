CFLAGS = -W -Wall -O3 -march=native -mtune=native
CXXFLAGS = -W -Wall -O3 -march=native -mtune=native
TARGETS := bfl
LDFLAGS = -L/usr/local/lib -llightning

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
