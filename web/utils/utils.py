def letter_to_number(self, text):
	text= text.upper()
	text = text.replace("ONE","1")
	text = text.replace("TWO","2")
	text = text.replace("THREE","3")
	text = text.replace("FOUR","4")
	text = text.replace("FIVE","5")
	text = text.replace("SIX","6")
	text = text.replace("SEVEN","7")
	text = text.replace("EIGHT","8")
	text = text.replace("NINE","9")
	text = text.replace("ZERO","0")
	return text