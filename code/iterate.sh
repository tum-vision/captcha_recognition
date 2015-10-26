# these variables are only used for naming the tests
number=01
prefix="3_layers-10000_initial_images"
# the network files that we want to use
network="network_captchas_with_3_convolutional_layers_train"
network_test="network_captchas_with_3_convolutional_layers"

# The name must be different for every new test!
# NEVER EVER start two iterations with the same name at the same time ;)

mode="correct_mostuncertain"
#mode="correct_mostcertain"
#mode="correct_random"
#mode="wrong_mostuncertain"
#mode="wrong_mostcertain"
#mode="wrong_random"
name=$number"-"$prefix"-"$mode
# create folder for results
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

'''
mode="correct_mostcertain"
name=$number"_"$prefix"correct_mostcertain"
# create folder for results
rm -rf results/$name
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test > results/${name}/log.txt 2>&1


mode="correct_random"
name=$number"_"$prefix"correct_random"
# create folder for results
rm -rf results/$name
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test > results/${name}/log.txt 2>&1


mode="wrong_mostcertain"
name=$number"_"$prefix"wrong_mostcertain"
# create folder for results
rm -rf results/$name
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test > results/${name}/log.txt 2>&1


mode="wrong_mostuncertain"
name=$number"_"$prefix"wrong_mostuncertain"
# create folder for results
rm -rf results/$name
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test > results/${name}/log.txt 2>&1


mode="wrong_random"
name=$number"_"$prefix"wrong_random"
# create folder for results
rm -rf results/$name
mkdir results/$name
# the program will be started in the background.
./src/iterate.sh $name $mode $network $network_test > results/${name}/log.txt 2>&1
'''