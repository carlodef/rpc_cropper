all: srtm4.o geoid_height_wrapper.o Geoid.o
	gcc srtm4.o geoid_height_wrapper.o Geoid.o -ltiff -lm -lstdc++ -o srtm4

geoid_height_wrapper.o: geoid_height_wrapper.cpp
	g++ -c -g -O3 geoid_height_wrapper.cpp

Geoid.o: Geoid.cpp
	g++ -c -g -O3 Geoid.cpp -I.

srtm4.o: srtm4.c
	gcc -c -g -O3 -std=c99 -DNDEBUG -DMAIN_SRTM4 srtm4.c

clean:
	rm *.o
	rm srtm4
	rm *.pyc
