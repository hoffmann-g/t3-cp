CC = gcc
MPICC = mpicc
CFLAGS = -O2 -Wall

SRC_DIR = ../src

.PHONY: all clean

all: bs_seq dc_mpi dc_artigo_mpi

bs_seq: $(SRC_DIR)/bs_seq.c
	$(CC) $(CFLAGS) -o $@ $<

dc_mpi: $(SRC_DIR)/dc_mpi.c
	$(MPICC) $(CFLAGS) -o $@ $<

dc_artigo_mpi: $(SRC_DIR)/dc_artigo_mpi.c
	$(MPICC) $(CFLAGS) -o $@ $<

clean:
	rm -f bs_seq dc_mpi dc_artigo_mpi
