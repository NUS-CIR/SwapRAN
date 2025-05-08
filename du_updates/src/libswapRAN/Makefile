CC = gcc
CFLAGS = -Wall -fPIC
LDFLAGS = -shared
TARGET = libswapRAN.so
SRC = swapRAN.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)