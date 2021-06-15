import petl as etl
import sqlite3
from textblob import TextBlob
import plotly.plotly as py
import plotly
from plotly.graph_objs import *



conn= sqlite3.connect('billboard_top100.db')
cur= conn.cursor()

billboard_top100= etl.fromcsv("billboard_lyrics_1964-2015-2.csv", encoding="ISO-8859-1")


create_songs= "CREATE TABLE IF NOT EXISTS Songs (id INTEGER PRIMARY KEY AUTOINCREMENT, Rank TEXT, Song TEXT, Artist TEXT, Year TEXT, Lyrics TEXT)"
cur.execute(create_songs)

cut_data= etl.cut(billboard_top100, "Rank", "Song", "Artist", "Year", "Lyrics")
etl.todb(cut_data, conn, 'Songs')


select_lyrics= "SELECT Year, Lyrics from Songs"
cur.execute(select_lyrics)
lyrics_list= cur.fetchall()



lyrics_dict= {}
for (x, y) in lyrics_list:
	if x not in lyrics_dict.keys():
		lyrics_dict[x]= [y]
	else:
		lyrics_dict[x].append(y)





decade1= ["1965", "1966", "1967", "1968", "1969", "1970", "1971", "1972", "1973", "1974", "1975"]
decade2= ["1976", "1977", "1978", "1979", "1980", "1981", "1982", "1983", "1984", "1985"]
decade3= ["1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995"]
decade4= ["1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005"]
decade5= ["2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015"]




def analyze_sentiment(decade_list):
	for key in lyrics_dict.keys():
		if key in decade_list:
			t= " ".join(lyrics_dict[key])
			blob= TextBlob(t)
	return str(blob.sentiment).strip("Sentiment()")



sentiments_dict= {"1965-1975":analyze_sentiment(decade1), "1975-1985": analyze_sentiment(decade2), "1985-1995":analyze_sentiment(decade3), "1995-2005":analyze_sentiment(decade4), "2005-2015":analyze_sentiment(decade5)}




create_sentiments= "CREATE TABLE IF NOT EXISTS Sentiments (decade TEXT, polarity INT, subjectivity INT)"
cur.execute(create_sentiments)




insert_sentiments= "INSERT INTO Sentiments VALUES (?, ?, ?)"


for key in sentiments_dict.keys():
	split_value= sentiments_dict[key].split(",")
	values_list= [key, float(split_value[0][9:]), float(split_value[1][14:])]
	cur.execute(insert_sentiments, values_list)






select_polarity= "SELECT polarity from Sentiments ORDER BY decade ASC"
cur.execute(select_polarity)
pol= cur.fetchall()
polarity_forplot= [x for (x,) in pol]


select_decade= "SELECT decade from Sentiments"
cur.execute(select_decade)
dec= cur.fetchall()
decade_forplot= sorted([x for (x,) in dec])



plotly.tools.set_credentials_file(username='taylun', api_key='vcbBbZDrmKyurGgNTlxt') 
trace1= Scatter(x= decade_forplot, y= polarity_forplot, marker={'color': 'red','size': "10"})
data= Data([trace1])
layout= Layout(xaxis= {"title":"Decades"}, yaxis= {"title":"polarity"})
fig= Figure(data= data, layout= layout)

py.plot(fig, filename= "330-final-project")








conn.commit()
conn.close()


