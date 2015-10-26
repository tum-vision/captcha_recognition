## !/usr/bin/env sh
# Create lmdb database

# get variables
name=$1
caffe=$2

logAfterEveryFiles=1000


TRAIN=temp/${name}/train.txt
TRAIN_DATA_ROOT=temp/${name}/train_files/
TRAIN_DB=temp/${name}/train_db


# Set RESIZE=true to resize the images. Leave as false if
# images have already been resized using another tool.
RESIZE=false
if $RESIZE; then
	RESIZE_HEIGHT=256
	RESIZE_WIDTH=256
else
	RESIZE_HEIGHT=0
	RESIZE_WIDTH=0
fi

if [ ! -d "$TRAIN_DATA_ROOT" ]; then
	echo "Error: TRAIN_DATA_ROOT is not a path to a directory."
	exit 1
fi



# This function maps a character to a number.
# 0 -> 0, 1->1, ... 9->9, A->10, B->11, ... Z->35, 
# a->37, b->38, ... z->62
# there is a small mistkate! The class 36 is never asigned. But it doesn't matter ;)
convertCharacterToOutput(){
	ascii_value=$(printf '%d' "'$1")
	# a small letter
	if [ "$ascii_value" -gt 90 ]; then
		value=$((ascii_value-60))
	else
		# a big letter
		if [ "$ascii_value" -gt 57 ]; then
			value=$((ascii_value-55))
		# a digit
		else
			value=$((ascii_value-48)) 
		fi 
	fi
	return $value
}


echo "Creating $TRAIN"

# first empty the text file
cat /dev/null > $TRAIN

# write all file names into the text file
n=0
for name in $TRAIN_DATA_ROOT*; do
	filename=$(basename "$name")
	extension="${filename##*.}"
	filename="${filename%.*}"
	captcha_length=${#filename}
	for (( i=0; i<$captcha_length; i++ )); do
		character=${filename:$i:1}
		convertCharacterToOutput $character
		asciivalue=$?
		asciivalue=$((asciivalue + 63*i))
		echo $filename"."$extension" "$asciivalue >> $TRAIN
	done
	if (( $n % $logAfterEveryFiles == 0 )); then
		echo $n" files have been processed."
	fi
	n=$((n+1))
done


echo "Creating train lmdb..."

# cleanup: Remove old database
rm -rf $TRAIN_DB

GLOG_logtostderr=1 $caffe/build/tools/convert_imageset \
	--gray \
	--resize_height=$RESIZE_HEIGHT \
	--resize_width=$RESIZE_WIDTH \
	--shuffle \
	$TRAIN_DATA_ROOT \
	$TRAIN \
	$TRAIN_DB



echo "lmdb database created successful."