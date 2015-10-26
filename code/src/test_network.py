import sys
name = sys.argv[1]
iteration = sys.argv[2]
iteration_previous = sys.argv[3]
mode = sys.argv[4]
newTrainingImagesInEveryIteration = int(sys.argv[5])
network = "src/" + sys.argv[6] + ".prototxt"
caffe_root = sys.argv[7]

# We need to define how many digits our CAPTCHAs can have at maximum.
# For simplicity we only have CAPTCHAs of fixed length 6 in this version!
maxNumberOfDigits = 6
logAfterEveryFiles = 1000


folder = "temp/" + name + "/learning_files/"
folder_new = "temp/" + name + "/train_files/"
folder_final_val = "temp/" + name + "/final_val_files/"
folder_results = "results/" + name + "/"


model = 'temp/' + name + '/results/data_iter_' + iteration + '.caffemodel'

import numpy as np
# show whole arrays in outputs
np.set_printoptions(threshold=np.nan)
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, caffe_root + 'python')
import caffe
import time
import os

from math import log
from sklearn import svm, datasets
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from random import shuffle

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# for copy
import shutil



# This function maps the ascii value of a character to a number.
# 0 -> 0, 1->1, ... 9->9, A->10, B->11, ... Z->35, 
# a->37, b->38, ... z->62
# there is a small mistkate! The class 36 is never asigned. But it doesn't matter ;)
def convertCharacterToClass(ascii_value):
	if ascii_value > 90:
		# a small letter
		correctClass = ascii_value-60
	elif ascii_value > 57:
		# a big letter
		correctClass = ascii_value-55
	else:
		# a digit
		correctClass=ascii_value-48
	return correctClass
	
# This function is the inverse function of convertCharacterToClass
def convertClassToCharacter(predictedClass):
	if predictedClass < 10:
		predictedCharacter = chr(predictedClass+48)
		#print 'Predicted digit:', predictedCharacter
	elif predictedClass <= 36:
		predictedCharacter = chr(predictedClass+55)
		#print "Predicted big letter", predictedCharacter
	else:
		predictedCharacter = chr(predictedClass+60)
		#print "Predicted small letter", predictedCharacter
	return predictedCharacter;



# if we do not want an extra testing set, but are also ok with just the result of the learning images (Output_learning_accuracy.txt), we can set this to False
# if true, we calculate the accuracy with the files in folder_final_val
if True:
	testAfterEveryIterations = 5000
	for test_iteration in range(int(iteration_previous)+testAfterEveryIterations,int(iteration)+testAfterEveryIterations,testAfterEveryIterations):
		
		test_iteration=str(test_iteration)
		print("Testing iteration {0} with final validation images...".format(test_iteration))
		
		folder_results_iteration = folder_results + test_iteration + "/"
		model = 'temp/' + name + '/results/data_iter_' + test_iteration + '.caffemodel'
		solverstate = 'temp/' + name + '/results/data_iter_' + test_iteration + '.solverstate'
		
		
		# Make classifier.
		classifier = caffe.Classifier(network,model,gpu=True,mean=None)
		
		
		numberOfCorrectClassified = 0
		numberOfNearlyCorrectClassified = 0
		numberOfTestedFiles = 0
		predictedClassesArray = [[] for i in range(maxNumberOfDigits)]
		correctClassesArray = [[] for i in range(maxNumberOfDigits)]
		uncertaintyCorrectDigits = []
		uncertaintyWrongDigits = []
		#squaredUncertaintyCorrectDigits = []
		#squaredUncertaintyWrongDigits = []
		#entropyCorrectDigits = []
		#entropyWrongDigits = []
		#correctImages = []
		#wrongImages = []
		overallentropy = 0
		overalluncertainty = 0
		overallsquaredUncertainty = 0
		
		start = time.time()
		for file in os.listdir(folder_final_val):
			IMAGE_FILE = folder_final_val + file
			#print(IMAGE_FILE)
			correctString = os.path.splitext(file)[0]
			#convert the string into a list of chars
			correctChars = list(correctString)
			
			input_image = caffe.io.load_image(IMAGE_FILE, color=False)
			
			# convert image to grayscale with 1 channel if it is saved with 3 channels
			# We assume that all three channels are identical and thus just take the second channel and ignore the others
			if input_image.shape[2]>1:
				#print "Converting image to grayscale"
				input_image = input_image[:,:,1]
				input_image = np.reshape(input_image, (50,180,1))
			
			# print input_image
			inputs = [input_image]
			
			# Classify.
			prediction = classifier.predict(inputs, oversample=False)
			
			predictedString = ""
			numberOfDigits = 6
			classesPerDigit = 63
			numberOfCorrectChars = 0
			
			entropy = 0
			uncertainty = 0
			squaredUncertainty = 0
			
			for x in xrange(0, numberOfDigits):
				
				predictedChar = prediction[0][63*x:63*(x+1)]
				
				# normalize to a sum of 1
				predictedChar = predictedChar * sum(predictedChar) ** -1
				
				# first guess
				predictedClass = predictedChar.argmax()
				probabilityFirst = predictedChar.max()
				predictedCharacter = convertClassToCharacter(predictedClass)
				predictedString+=predictedCharacter
				
				# secondguess
				predictedChar[predictedClass]=0
				predictedClassSecond = predictedChar.argmax()
				probabilitySecond = predictedChar.max()
				predictedCharacterSecond = convertClassToCharacter(predictedClassSecond)
				
				# unceartainty: 0: absolutley certatin, 1: absoluteley uncertain
				uncertainty = uncertainty + probabilitySecond / probabilityFirst
				
				# calculate entropy
				for probability in predictedChar:
					if probability != 0:
						entropy = entropy + probability * log(probability, 2)
				
				# calculate squared uncertainty
				squaredUncertainty = squaredUncertainty + (1 - probabilityFirst) ** 2
				
				# was this character predicted correct?
				if predictedCharacter == correctChars[x]:
					numberOfCorrectChars+=1
				
				
				# for confusion matrix: get correct class:
				ascii_value = ord(correctChars[x])
				correctClass = convertCharacterToClass(ascii_value)
				
				# save correct class
				correctClassesArray[x].append(correctClass)
				# and save predicted classs
				predictedClassesArray[x].append(predictedClass)
				
			
			uncertainty = uncertainty / numberOfDigits
			entropy = -entropy / log(63, 2) / numberOfDigits
			squaredUncertainty = squaredUncertainty / numberOfDigits
			
			overallentropy = overallentropy + entropy
			overalluncertainty = overalluncertainty + uncertainty
			overallsquaredUncertainty = overallsquaredUncertainty + squaredUncertainty
			
			# was the whole sequence predicted correct?
			if predictedString == correctString:
				numberOfCorrectClassified+=1
				#correctImages.append(folder + file)
				uncertaintyCorrectDigits.append(uncertainty)
				#squaredUncertaintyCorrectDigits.append(squaredUncertainty)
				#entropyCorrectDigits.append(entropy)
			else:
				#wrongImages.append(folder + file)
				uncertaintyWrongDigits.append(uncertainty)
				#squaredUncertaintyWrongDigits.append(squaredUncertainty)
				#entropyWrongDigits.append(entropy)
			
			# was only at most one character wrong?
			if numberOfCorrectChars >= numberOfDigits-1:
				numberOfNearlyCorrectClassified+=1
			
			numberOfTestedFiles+=1
			if numberOfTestedFiles % logAfterEveryFiles == 0:
				print("{0} files have been processed".format(numberOfTestedFiles))
	
		#print "Done in %.2f s." % (time.time() - start)
		
		print("{0} of {1} CAPTCHAs have been classified correctly ({2:2.2f}%)".format(
		numberOfCorrectClassified, numberOfTestedFiles, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
		#print("{0} of {1} CAPTCHAs have been classified nearly correctly (at most 1 character wrong) ({2:2.2f}%)".format(
		#numberOfNearlyCorrectClassified, numberOfTestedFiles, float(numberOfNearlyCorrectClassified) / numberOfTestedFiles*100))
		
		# write accuracy into the file Output.txt (nicely human readable)
		text_file = open(folder_results + "Output_accuracy.txt", "a")
		text_file.write("{0}: {1:2.2f}%\n".format(test_iteration, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
		text_file.close()
		
		# write accuracy into the file Output2.txt (nicely to copy into Matlab)
		text_file = open(folder_results + "Output_accuracy_matlab.txt", "a")
		text_file.write(",{1:2.2f}".format(test_iteration, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
		text_file.close()
		
		# compute the overall entropy, uncertainty and squared uncertaintyy
		overallentropy = overallentropy / numberOfTestedFiles
		overalluncertainty = overalluncertainty / numberOfTestedFiles
		overallsquaredUncertainty = overallsquaredUncertainty / numberOfTestedFiles
		
		# save overall entropy to the file Output_entropy.txt
		text_file = open(folder_results + "Output_entropy.txt", "a")
		text_file.write("{1:2.2f},".format(test_iteration, overallentropy))
		text_file.close()
		
		# save overall uncertainty to the file Output_uncertainty.txt
		text_file = open(folder_results + "Output_uncertainty.txt", "a")
		text_file.write("{1:2.2f},".format(test_iteration, overalluncertainty))
		text_file.close()
		
		# save overall squared uncertainty to the file Output_squareduncertainty.txt
		text_file = open(folder_results + "Output_squareduncertainty.txt", "a")
		text_file.write("{1:2.2f},".format(test_iteration, overallsquaredUncertainty))
		text_file.close()
		
		# create the folder for the plots (confusion matrices and uncertainty histograms)
		if not os.path.exists(folder_results_iteration):
			os.makedirs(folder_results_iteration)
		
		# save histograms for uncertainty
		if len(uncertaintyCorrectDigits)>0 :
			plt.figure()
			plt.hist(uncertaintyCorrectDigits);
			plt.title("Histogram: Uncertainty for correct sequences")
			plt.savefig(folder_results_iteration + 'uncertainty_histogram_for_correct_classified_digits.png', dpi=200)
		
		if len(uncertaintyWrongDigits)>0 :
			plt.figure()
			plt.hist(uncertaintyWrongDigits);
			plt.title("Histogram: Uncertainty for wrong sequences")
			plt.savefig(folder_results_iteration + 'uncertainty_histogram_for_wrong_classified_digits.png', dpi=200)
		
		
		# save confusion matrices
		for (i, item) in enumerate(predictedClassesArray):
			cm = confusion_matrix(correctClassesArray[i],predictedClassesArray[i])
			cm2 = np.empty(cm.shape)
			for idx,row in enumerate(cm):
				#print(cm[0,:]/float(max(cm[0,:])))
				cm2[idx,:] = row/float(max(1,sum(row)))
			
			plt.matshow(cm2)
			plt.title(`(i+1)` + '. Character')
			plt.colorbar()
			plt.ylabel('True label')
			plt.xlabel('Predicted label')
			plt.savefig(folder_results_iteration + 'confusion_matrix_for_digit_' + `(i+1)` + '.png', dpi=200)
			
		plt.close('all')

# delete temp files
if int(test_iteration) != int(iteration):
	print("Deleting {0}...".format(model))
	os.remove(model)
	os.remove(solverstate)







numberOfCorrectClassified = 0
numberOfNearlyCorrectClassified = 0
numberOfTestedFiles = 0
predictedClassesArray = [[] for i in range(maxNumberOfDigits)]
correctClassesArray = [[] for i in range(maxNumberOfDigits)]
uncertaintyCorrectDigits = []
uncertaintyWrongDigits = []
#squaredUncertaintyCorrectDigits = []
#squaredUncertaintyWrongDigits = []
#entropyCorrectDigits = []
#entropyWrongDigits = []
correctImages = []
wrongImages = []
overallentropy = 0
overalluncertainty = 0
overallsquaredUncertainty = 0

print "Testing learning images..."
start = time.time()
for file in os.listdir(folder):
	IMAGE_FILE = folder + file
	#print(IMAGE_FILE)
	correctString = os.path.splitext(file)[0]
	#convert the string into a list of chars
	correctChars = list(correctString)
	
	input_image = caffe.io.load_image(IMAGE_FILE, color=False)
	
	# convert image to grayscale with 1 channel if it is saved with 3 channels
	# We assume that all three channels are identical and thus just take the second channel and ignore the others
	if input_image.shape[2]>1:
		#print "Converting image to grayscale"
		input_image = input_image[:,:,1]
		input_image = np.reshape(input_image, (50,180,1))
	
	# print input_image
	inputs = [input_image]
	
	# Classify.
	prediction = classifier.predict(inputs, oversample=False)
	
	predictedString = ""
	numberOfDigits = 6
	classesPerDigit = 63
	numberOfCorrectChars = 0
	
	entropy = 0
	uncertainty = 0
	squaredUncertainty = 0
	
	for x in xrange(0, numberOfDigits):
		
		predictedChar = prediction[0][63*x:63*(x+1)]
		
		# normalize to a sum of 1
		predictedChar = predictedChar * sum(predictedChar) ** -1
		
		# first guess
		predictedClass = predictedChar.argmax()
		probabilityFirst = predictedChar.max()
		predictedCharacter = convertClassToCharacter(predictedClass)
		predictedString+=predictedCharacter
		
		# secondguess
		predictedChar[predictedClass]=0
		predictedClassSecond = predictedChar.argmax()
		probabilitySecond = predictedChar.max()
		predictedCharacterSecond = convertClassToCharacter(predictedClassSecond)
		
		# unceartainty: 0: absolutley certatin, 1: absoluteley uncertain
		uncertainty = uncertainty + probabilitySecond / probabilityFirst
		
		# calculate entropy
		for probability in predictedChar:
			if probability != 0:
				entropy = entropy + probability * log(probability, 2)
		
		# calculate squared uncertainty
		squaredUncertainty = squaredUncertainty + (1 - probabilityFirst) ** 2
		
		# was this character predicted correct?
		if predictedCharacter == correctChars[x]:
			numberOfCorrectChars+=1
		
		
		# for confusion matrix: get correct class:
		ascii_value = ord(correctChars[x])
		correctClass = convertCharacterToClass(ascii_value)
		
		# save correct class
		correctClassesArray[x].append(correctClass)
		# and save predicted classs
		predictedClassesArray[x].append(predictedClass)
		
	
	
	uncertainty = uncertainty / numberOfDigits
	entropy = -entropy / log(63, 2) / numberOfDigits
	squaredUncertainty = squaredUncertainty / numberOfDigits
	
	overallentropy = overallentropy + entropy
	overalluncertainty = overalluncertainty + uncertainty
	overallsquaredUncertainty = overallsquaredUncertainty + squaredUncertainty
	
	# was the whole sequence predicted correct?
	if predictedString == correctString:
		numberOfCorrectClassified+=1
		correctImages.append(folder + file)
		uncertaintyCorrectDigits.append(uncertainty)
		#squaredUncertaintyCorrectDigits.append(squaredUncertainty)
		#entropyCorrectDigits.append(entropy)
	else:
		wrongImages.append(folder + file)
		uncertaintyWrongDigits.append(uncertainty)
		#squaredUncertaintyWrongDigits.append(squaredUncertainty)
		#entropyWrongDigits.append(entropy)
	
	# was only at most one character wrong?
	if numberOfCorrectChars >= numberOfDigits-1:
		numberOfNearlyCorrectClassified+=1
	
	numberOfTestedFiles+=1
	if numberOfTestedFiles % logAfterEveryFiles == 0:
		print("{0} files have been processed".format(numberOfTestedFiles))

	 
print "Done in %.2f s." % (time.time() - start)

print("{0} of {1} CAPTCHAs have been classified correctly ({2:2.2f}%)".format(
numberOfCorrectClassified, numberOfTestedFiles, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
print("{0} of {1} CAPTCHAs have been classified nearly correctly (at most 1 character wrong) ({2:2.2f}%)".format(
numberOfNearlyCorrectClassified, numberOfTestedFiles, float(numberOfNearlyCorrectClassified) / numberOfTestedFiles*100))


# sort trainImages (which will get the new training images in the next iteration)
print("Sorting files...")
if mode=="wrong_mostcertain":
	sorting = sorted(zip(uncertaintyWrongDigits,wrongImages), reverse=False)
elif mode=="wrong_mostuncertain":
	sorting = sorted(zip(uncertaintyWrongDigits,wrongImages), reverse=True)
elif mode=="wrong_random":
	sorting = zip(uncertaintyWrongDigits,wrongImages)
	shuffle(sorting)
elif mode=="correct_mostcertain":
	sorting = sorted(zip(uncertaintyCorrectDigits,correctImages), reverse=False)
elif mode=="correct_mostuncertain":
	sorting = sorted(zip(uncertaintyCorrectDigits,correctImages), reverse=True)
elif mode=="correct_random":
	sorting = zip(uncertaintyCorrectDigits,correctImages)
	shuffle(sorting)
else:
	print("No correct mode has been selected")
	sys.exit(0)

trainImages = [y for x,y in sorting]
#uncertaintyCorrectDigits = [x for (x,y) in sorting]

# copy the $newTrainingImagesInEveryIteration (10000) first images (which will get the new training images in the next iteration)
i=0
for (i, item) in enumerate(trainImages):
	#print("file {0} has uncertainty {1}".format(trainImages[i], i))
	shutil.copy2(item, folder_new)
	if i % logAfterEveryFiles == 0:
		print("{0} files have been copied".format(i))
	if i==newTrainingImagesInEveryIteration-1:
		break

# if less than newTrainingImagesInEveryIteration (10000) wrong images were available, copy the rest from the correct images
# If we are reaching a very high accuracy, this is very likely to happen.
if mode=="wrong_mostcertain" or mode=="wrong_mostuncertain" or mode=="wrong_random":
	if i < newTrainingImagesInEveryIteration-1:
		print("Sorting files 2...")
		sorting = sorted(zip(uncertaintyCorrectDigits,correctImages), reverse=True)
		trainImages = [y for x,y in sorting]
		for j in xrange(i, newTrainingImagesInEveryIteration-1):
			shutil.copy2(trainImages[j-i], folder_new)
			if (j-i) % logAfterEveryFiles == 0:
				print("{0} additional correct files have been copied".format(j-i))



# write accuracy into the file Output.txt (nicely human readable)
text_file = open(folder_results + "Output_learning_accuracy.txt", "a")
text_file.write("{0}: {1:2.2f}%\n".format(iteration, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
text_file.close()

# write accuracy into the file Output2.txt (nicely to copy into Matlab)
text_file = open(folder_results + "Output_learning_accuracy_matlab.txt", "a")
text_file.write("{1:2.2f},".format(iteration, float(numberOfCorrectClassified) / numberOfTestedFiles*100))
text_file.close()

# compute the overall entropy, uncertainty and squared uncertaintyy
overallentropy = overallentropy / numberOfTestedFiles
overalluncertainty = overalluncertainty / numberOfTestedFiles
overallsquaredUncertainty = overallsquaredUncertainty / numberOfTestedFiles

# save overall entropy to the file Output_entropy.txt
text_file = open(folder_results + "Output_learning_entropy.txt", "a")
text_file.write("{1:2.2f},".format(iteration, overallentropy))
text_file.close()

# save overall uncertainty to the file Output_uncertainty.txt
text_file = open(folder_results + "Output_learning_uncertainty.txt", "a")
text_file.write("{1:2.2f},".format(iteration, overalluncertainty))
text_file.close()

# save overall squared uncertainty to the file Output_squareduncertainty.txt
text_file = open(folder_results + "Output_learning_squareduncertainty.txt", "a")
text_file.write("{1:2.2f},".format(iteration, overallsquaredUncertainty))
text_file.close()



# Delete temp files from last iteration
if int(iteration_previous) > 0:
	model = 'temp/' + name + '/results/data_iter_' + iteration_previous + '.caffemodel'
	solverstate = 'temp/' + name + '/results/data_iter_' + iteration_previous + '.solverstate'
	print("Deleting {0}...".format(model))
	os.remove(model)
	os.remove(solverstate)