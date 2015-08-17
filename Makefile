CFLAGS = -W -Wall
CXXFLAGS = -W -Wall
TARGETS := bfl bflo
LDFLAGS = -llightning

all: $(TARGETS)

clean:
	rm -f $(TARGETS)
