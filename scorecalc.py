import messages

def fiftymetre_score(timeInSeconds):
	if(timeInSeconds <= 8.0):
	 	return 10
	elif(timeInSeconds <= 8.4):
	 	return 9
	elif(timeInSeconds <= 8.8):
		return 8
	elif(timeInSeconds <= 9.2):
		return 7
	elif(timeInSeconds <= 9.6):
		return 6
	elif(timeInSeconds <= 10):
		return 5
	elif(timeInSeconds <= 10.4):
		return 4
	elif(timeInSeconds <= 10.8):
		return 3
	elif(timeInSeconds <= 11.2):
		return 2
	elif(timeInSeconds <= 11.6):
		return 1
	else :
		return 0

def eighthundredmetre_score(timeInSeconds):
	if(timeInSeconds <= 3.17):
		return 10
	elif(timeInSeconds <= 3.32):
		return 9
	elif(timeInSeconds <= 3.47):
		return 8
	elif(timeInSeconds <= 4.02):
		return 7
	elif(timeInSeconds <= 4.17):
		return 6
	elif(timeInSeconds <= 4.32):
		return 5
	elif(timeInSeconds <= 4.47):
		return 4
	elif(timeInSeconds <= 5.02):
		return 3
	elif(timeInSeconds <= 5.17):
		return 2
	elif(timeInSeconds <= 5.32):
		return 1
	else:
		return 0

def shotput_score(distanceInMetres):
	if(distanceInMetres >= 4.66):
		return 10
	elif(distanceInMetres >= 4.31):
		return 9
	elif(distanceInMetres >= 3.96):
		return 8
	elif(distanceInMetres >= 3.61):
		return 7
	elif(distanceInMetres >= 3.26):
		return 6
	elif(distanceInMetres >= 2.91):
		return 5
	elif(distanceInMetres >= 2.56):
		return 4
	elif(distanceInMetres >= 2.21):
		return 3
	elif(distanceInMetres >= 1.86):
		return 2
	elif(distanceInMetres >= 1.51):
		return 1
	else:
		return 0

def longjump_score(distanceInMetres):
	if(distanceInMetres >= 3.67):
		return 10
	elif(distanceInMetres >= 3.42):
		return 9
	elif(distanceInMetres >= 3.17):
		return 8
	elif(distanceInMetres >= 2.92):
		return 7
	elif(distanceInMetres >= 2.67):
		return 6
	elif(distanceInMetres >= 2.42):
		return 5
	elif(distanceInMetres >= 2.17):
		return 4
	elif(distanceInMetres >= 1.92):
		return 3
	elif(distanceInMetres >= 1.67):
		return 2
	elif(distanceInMetres >= 1.42):
		return 1
	else:
		return 0

def agilityScore(timeInSeconds):
	if(timeInSeconds <= 16.5):
		return 10
	elif(timeInSeconds <= 17.1):
		return 9
	elif(timeInSeconds <= 17.7):
		return 8
	elif(timeInSeconds <= 18.3):
		return 7
	elif(timeInSeconds <= 18.9):
		return 6
	elif(timeInSeconds <= 19.5):
		return 5
	elif(timeInSeconds <= 20.1):
		return 4
	elif(timeInSeconds <= 20.7):
		return 3
	elif(timeInSeconds <= 21.3):
		return 2
	elif(timeInSeconds <= 21.9):
		return 1
	else:
		return 0

def getRemarks(score):
	if(score > 5):
		return messages.DOING_WELL
	else:
		return messages.TO_IMPROVE