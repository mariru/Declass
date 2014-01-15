#assuming file structure
#	home/mariru/Installs/vowpal_wabbit-7.3/declass/declass
#					      /parallel_easy/parallel_easy
#	
#	home/mariru/DATA/cable_01/raw/bodyfiles
#				     /meta
#				 /processed
#			/kiss_01/raw/bodyfiles
#				    /meta
#				/processed

# assuming you are in folder   home/mariru/DATA/cable_01

# ipython

import sys
sys.path.append('/home/mariru/Installs/vowpal_wabbit-7.3/declass/')
sys.path.append('/home/mariru/Installs/vowpal_wabbit-7.3/parallel_easy/')

# A) Convert directory of text files to single file in vw format

from declass.utils.streamers import TextFileStreamer
from declass.utils.text_processors import TokenizerBasic

my_tokenizer = TokenizerBasic()
stream = TextFileStreamer(text_base_path='raw/bodyfiles', tokenizer=my_tokenizer)
stream.to_vw('processed/my_doc_tokens.vw', n_jobs=-1)

from declass.utils.text_processors import SFileFilter, VWFormatter
sff = SFileFilter(VWFormatter(),20)
sff.load_sfile('processed/my_doc_tokens.vw')

sff.filter_extremes(doc_freq_min=5, doc_fraction_max=0.7)

from nltk.corpus import wordnet
from nltk.corpus import stopwords

df = sff.to_frame()



remove_tokens=[]
for tok in df.index:
	if ( tok in stopwords.words('english') or not wordnet.synsets(tok)) :
		remove_tokens=remove_tokens+[tok]


#####	


monthnames=['january','jan','february','feb','march','mar','april','apr','may','june','jun','july','jul','august','aug','september','sep','november','nov','december','de','dec','para']

stop_words=["meeting","agreed","confidential","actually","remarks","lower","ad","back","wish","act","two","used","agency","fully","confirmed","ten","appreciate","quito","resolve","hours","trying","seen","feel","available","re","mr","mrs","hotel","done","underway","way","side","go","paragraph","percent","program","year","month","en","look","text","sure","secret","asap","young","real","positive","negative","continuing","states","refused","understand","continue","related","require","current","using","explained","status","full","mt","letter","next","results","concluded","immediate","nine","friday","statement","scheduled","present","question","week","thus","questions","perhaps","last","even","many","faced","details","another","allowed","subject","state","secretary"]

remove_words=[month for month in monthnames if month in df.index]+[stop for stop in stop_words if stop in df.index]

remove=list(set(remove_tokens+remove_words))

sff.filter_extremes(doc_freq_min=5, doc_fraction_max=0.8)
sff.filter_tokens(remove)
sff.compactify()
sff.save('my_sff_file.pkl')
sff.filter_sfile('processed/my_doc_tokens.vw', 'processed/my_doc_tokens_filtered.vw')


############ RUN LDA  ##########################################

#	rm -f *cache

#	vw --lda 50 --cache_file ddrs.cache --passes 4 -p prediction100.dat --readable_model topics100.dat --bit_precision 16 --lda_D 400000 --lda_rho 0.05 --lda_alpha 0.8 my_doc_tokens_filtered.vw

################################################################

from declass.utils.vw_helpers import LDAResults
num_topics = 100
lda1000 = LDAResults('processed/topics1000.dat', 'processed/prediction1000.dat', num_topics, 'my_sff_file.pkl')

fi=open("lda100-topics.txt","w+")
#lda70.print_topics(10,fi)
topic_text=fi.readlines()


import pandas as pn
import matplotlib.pyplot as plt
import dateutil.parser as dparser
import matplotlib.dates as mdates
from pandas import DataFrame

meta=pn.read_csv('raw/meta/meta.csv',sep='|')

dates=[dparser.parse(d) if type(d)==str else 0 for d in meta.date]


monthlify = lambda g : g.replace(day=1)
a=lda1000.pr_topic_g_doc
b=lda1000.pr_doc
important_classes=['CONFIDENTIAL','UNCLASSIFIED','LIMITED OFFICIAL USE','SECRET']

text_count=2

for n in xrange(100):
	txt="Top words: "
	for i in topic_text[text_count+1:text_count+16]:
		txt=txt+i.split()[0]+", "
	
	fig, ax = plt.subplots()
	column_name = topic_text[text_count].split()[0]
	file_name = topic_text[text_count+1].split()[0]+'-'+topic_text[text_count+2].split()[0]+'-'+topic_text[text_count+3].split()[0]
	text_count+=18
	column = a[column_name]
	pr_topic_dot_doc = [column[i]*b[i] if (i in column.index and i in b.index) else 0 for i in meta.doc_id]
	df=DataFrame({'date':dates,'prob':pr_topic_dot_doc,'class':meta.origclass})
	for cls in important_classes:
		dff=df[df['class']==cls]
		dff['date']= dff['date'].apply(monthlify)
		dff=dff.groupby('date')
		dff=dff.mean()
		if cls == 'SECRET':
			ax.plot_date(dff.index, dff['prob'],'r-',label=cls)
		if cls == 'CONFIDENTIAL':
			ax.plot_date(dff.index, dff['prob'],'m-',label=cls)
		if cls == 'LIMITED OFFICIAL USE':
			ax.plot_date(dff.index, dff['prob'],'y-',label=cls)
		if cls == 'UNCLASSIFIED':
			ax.plot_date(dff.index, dff['prob'],'c-',label=cls)
	df['date']= df['date'].apply(monthlify)
	df=df.groupby('date').mean()
	ax.plot_date(df.index, df['prob'],'k-', label='TOTAL')
	fig.autofmt_xdate()
	legend=ax.legend(loc='upper center')
	figure_name = "./"+file_name+".png"
	fig.set_size_inches(17,9, dpi=150)
	fig.text(0.1,0.05,txt)
	plt.savefig(figure_name)
	plt.close(fig)




