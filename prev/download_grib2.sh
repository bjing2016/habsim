LEVEL=1
LAT=33
LON=253

YEAR=2018
MONTH=3
DAY=7
HOUR=0

for HOUR in 0 3 6 9 12 15 18 21; do
	echo $HOUR
	YEAR_FMT=$(printf "%04d" $YEAR)
	MONTH_FMT=$(printf "%02d" $MONTH)
	DAY_FMT=$(printf "%02d" $DAY)
	HOUR_FMT=$(printf "%03d" $HOUR)
	OUT="wind-$YEAR_FMT-$MONTH_FMT-$DAY_FMT-$HOUR_FMT.txt"

	URL="https://nomads.ncdc.noaa.gov/data/gfs4/$YEAR_FMT$MONTH_FMT/$YEAR_FMT$MONTH_FMT$DAY_FMT/gfs_4_$YEAR_FMT$MONTH_FMT$DAY_FMT""_0000_$HOUR_FMT.grb2"
	FILE="gfs_4_$YEAR_FMT$MONTH_FMT$DAY_FMT""_0000_$HOUR_FMT.grb2"

	echo $URL
	echo $FILE

	wget $URL

	FILTER="^\s\+""$(printf %0.3f $LAT)""\s\+""$(printf %0.3f $LON)"

	echo "braaainnnz" > $OUT
	grib_get_data -p shortName,level -w shortName=u/v/t,typeOfFirstFixedSurface=100 $FILE | grep $FILTER | cut -d " " -f 7,8,9 >> $OUT

	rm $FILE
done
