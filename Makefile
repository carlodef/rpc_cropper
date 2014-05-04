all: srtm4.o iio.o geoid_height_wrapper.o Geoid.o
	cc srtm4.o iio.o geoid_height_wrapper.o Geoid.o -lpng -ltiff -ljpeg -lm -lstdc++ -o srtm4

geoid_height_wrapper.o: geoid_height_wrapper.cpp
	g++ -c -g -O3 geoid_height_wrapper.cpp

Geoid.o: Geoid.cpp
	g++ -c -g -O3 Geoid.cpp -I.

iio.o: iio.c iio.h
	cc -c -std=c99 -g -O3 -DNDEBUG -DDONT_USE_TEST_MAIN iio.c

srtm4.o: srtm4.c iio.h
	cc -c -std=c99 -g -O3 -DNDEBUG -DMAIN_SRTM4 srtm4.c

clean:
	rm *.o
	rm srtm4
