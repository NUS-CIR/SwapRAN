# Use Ubuntu 20.04 (glibc 2.31)
FROM ubuntu:20.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt update && \
    apt install -y build-essential make gcc && \
    apt clean

# Set working directory inside container
WORKDIR /build

# Copy source code into container
COPY . .

# Build the library using your Makefile
RUN make

# Optional: Show which GLIBC version the library was linked against
RUN ldd libswapRAN.so

# Final image just contains the built library
CMD ["bash"]
