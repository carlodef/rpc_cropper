all: srtm4 srtm4_which_tile

srtm4: Geoid.o geoid_height_wrapper.o srtm4.o
	gcc $^ -ltiff -lm -lstdc++ -o $@

srtm4_which_tile: Geoid.o geoid_height_wrapper.o srtm4_which_tile.o
	gcc $^ -ltiff -lm -lstdc++ -o $@

Geoid.o: Geoid.cpp
	g++ -c -g -O3 $^ -I. -o $@

geoid_height_wrapper.o: geoid_height_wrapper.cpp
	g++ -c -g -O3 $^ -I. -o $@

srtm4.o: srtm4.c
	gcc -c -g -O3 -std=c99 -DNDEBUG -DMAIN_SRTM4 $^ -o $@

srtm4_which_tile.o: srtm4.c
	gcc -c -g -O3 -std=c99 -DNDEBUG -DMAIN_SRTM4_WHICH_TILE $^ -o $@

clean:
	-rm *.o
	-rm srtm4
	-rm srtm4_which_tile
	-rm *.pyc
