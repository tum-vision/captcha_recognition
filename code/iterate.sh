# these variables are only used for naming the tests
number="01"
prefix="3_layers-10000_initial_images"

# the network files that we want to use
network="network_captchas_with_3_convolutional_layers_train"
network_test="network_captchas_with_3_convolutional_layers"

# The name must be different for every new test!
# NEVER EVER start two iterations with the same name at the same time ;)

# set permissions
chmod +x src/iterate.sh

mode="correct_mostuncertain"
#mode="correct_mostcertain"
#mode="correct_random"
#mode="wrong_mostuncertain"
#mode="wrong_mostcertain"
#mode="wrong_random"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

# uncommenting these lines results in every test being executed one after each other
'''
mode="correct_mostcertain"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

mode="correct_random"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

mode="wrong_mostuncertain"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

mode="wrong_mostcertain"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt

mode="wrong_random"
name=$number"-"$prefix"-"$mode
# create folder for results and start test
mkdir results/$name
./src/iterate.sh $name $mode $network $network_test >> results/${name}/log.txt 2>>results/${name}/log2.txt
'''