CFLAGS = -W -Wall -g
CXXFLAGS = -W -Wall -g
TARGETS := bfl
LDFLAGS = -L/usr/local/lib -llightning

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
